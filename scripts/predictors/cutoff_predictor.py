import pandas as pd


class CutoffPredictor:

    def __init__(self, csv_dir):

        self.cutoffs = pd.read_csv(
            csv_dir / "cutoffs.csv"
        )

        self.colleges = pd.read_csv(
            csv_dir / "colleges.csv"
        )

        self.branches = pd.read_csv(
            csv_dir / "branches.csv"
        )

    # ==========================================================
    # DATA PREPARATION
    # ==========================================================

    def prepare_cutoffs(self):

        data = self.cutoffs.copy()

        # ------------------------------------------------------
        # Remove known unavailable / NA sentinel values
        # ------------------------------------------------------

        data.loc[
            (data["year"] == 2023) &
            (data["closingRank"] == 156852),
            "closingRank"
        ] = pd.NA

        data.loc[
            (data["year"] == 2024) &
            (data["closingRank"] == 180374),
            "closingRank"
        ] = pd.NA

        data = data.dropna(
            subset=["closingRank"]
        ).copy()

        data["closingRank"] = pd.to_numeric(
            data["closingRank"],
            errors="coerce"
        )

        data = data.dropna(
            subset=["closingRank"]
        ).copy()

        return data

    # ==========================================================
    # FINAL CUT-OFF DATA
    # ==========================================================

    def final_cutoffs(self):

        data = self.prepare_cutoffs()

        return data[
            data["phase"] == "Final"
        ].copy()

    # ==========================================================
    # HISTORICAL CUTOFF SUMMARY
    # ==========================================================

    def historical_cutoffs(self):

        data = self.final_cutoffs()

        return (
            data
            .groupby(
                [
                    "collegeCode",
                    "branchCode",
                    "category"
                ]
            )
            .agg(
                years=("year", "count"),
                cutoff_min=("closingRank", "min"),
                cutoff_max=("closingRank", "max"),
                cutoff_mean=("closingRank", "mean")
            )
            .reset_index()
        )

    # ==========================================================
    # YEARLY CUTOFFS
    # ==========================================================

    def yearly_cutoffs(self):

        data = self.final_cutoffs()

        return (
            data
            .sort_values("year")
            [
                [
                    "year",
                    "collegeCode",
                    "branchCode",
                    "category",
                    "closingRank"
                ]
            ]
            .reset_index(drop=True)
        )

    # ==========================================================
    # LATEST CUTOFF
    # ==========================================================

    def latest_cutoffs(self):

        data = self.yearly_cutoffs()

        latest = (
            data
            .sort_values("year")
            .groupby(
                [
                    "collegeCode",
                    "branchCode",
                    "category"
                ],
                as_index=False
            )
            .tail(1)
        )

        return latest[
            [
                "collegeCode",
                "branchCode",
                "category",
                "year",
                "closingRank"
            ]
        ].rename(
            columns={
                "year": "latest_year",
                "closingRank": "latest_cutoff"
            }
        )

    # ==========================================================
    # FORECAST CUTOFFS
    # ==========================================================

    def forecast_cutoffs(self):

        data = self.yearly_cutoffs()

        pivot = (
            data
            .pivot_table(
                index=[
                    "collegeCode",
                    "branchCode",
                    "category"
                ],
                columns="year",
                values="closingRank",
                aggfunc="mean"
            )
            .reset_index()
        )

        # Make sure expected historical-year columns exist

        if 2023 not in pivot.columns:
            pivot[2023] = pd.NA

        if 2024 not in pivot.columns:
            pivot[2024] = pd.NA

        # Initialize prediction fields

        pivot["predicted_cutoff"] = pd.NA
        pivot["years_available"] = 0
        pivot["evidence_level"] = "Insufficient"

        # ------------------------------------------------------
        # 2023 + 2024 available
        #
        # Forecast = 70% of 2023 + 30% of 2024
        # ------------------------------------------------------

        both_years = (
            pivot[2023].notna() &
            pivot[2024].notna()
        )

        pivot.loc[
            both_years,
            "predicted_cutoff"
        ] = (
            pivot.loc[both_years, 2023] * 0.7
            +
            pivot.loc[both_years, 2024] * 0.3
        )

        pivot.loc[
            both_years,
            "years_available"
        ] = 2

        pivot.loc[
            both_years,
            "evidence_level"
        ] = "Strong"

        # ------------------------------------------------------
        # Only 2023 available
        # ------------------------------------------------------

        only_2023 = (
            pivot[2023].notna() &
            pivot[2024].isna()
        )

        pivot.loc[
            only_2023,
            "predicted_cutoff"
        ] = pivot.loc[
            only_2023,
            2023
        ]

        pivot.loc[
            only_2023,
            "years_available"
        ] = 1

        pivot.loc[
            only_2023,
            "evidence_level"
        ] = "Limited"

        # ------------------------------------------------------
        # Only 2024 available
        # ------------------------------------------------------

        only_2024 = (
            pivot[2023].isna() &
            pivot[2024].notna()
        )

        pivot.loc[
            only_2024,
            "predicted_cutoff"
        ] = pivot.loc[
            only_2024,
            2024
        ]

        pivot.loc[
            only_2024,
            "years_available"
        ] = 1

        pivot.loc[
            only_2024,
            "evidence_level"
        ] = "Limited"

        return pivot[
            [
                "collegeCode",
                "branchCode",
                "category",
                "predicted_cutoff",
                "years_available",
                "evidence_level"
            ]
        ].copy()

    # ==========================================================
    # CHANCE CLASSIFICATION
    # ==========================================================

    def classify_chance(self, rank_ratio):
        """
        Classify admission position using:

            rank_ratio = student_rank / predicted_cutoff

        Lower ratio = stronger position.

        Thresholds:

            <= 0.60  -> Very Favorable
            <= 0.75  -> Favorable
            <= 0.90  -> Competitive
            <= 1.00  -> Borderline
            >  1.00  -> Reach
        """

        if pd.isna(rank_ratio):
            return "Unknown"

        if rank_ratio <= 0.60:
            return "Very Favorable"

        elif rank_ratio <= 0.75:
            return "Favorable"

        elif rank_ratio <= 0.90:
            return "Competitive"

        elif rank_ratio <= 1.00:
            return "Borderline"

        else:
            return "Reach"

    # ==========================================================
    # RECOMMENDATION ORDERING
    # ==========================================================

    def _sort_recommendations(
        self,
        data,
        student_rank
    ):
        """
        Rank recommendations according to the student's
        actual rank position relative to the predicted cutoff.

        Core rule:

            cutoff_gap = predicted_cutoff - student_rank

        If cutoff_gap >= 0:
            The student's rank is within the predicted
            closing-rank range.

            These are realistic options.

        If cutoff_gap < 0:
            The student's rank is worse than the predicted
            closing rank.

            These are reach options.

        Primary ranking:

            1. Realistic options first
            2. Closest predicted cutoff to student's rank
            3. Stronger historical evidence
            4. Smaller predicted cutoff as tie-breaker

        No prestige score is used.
        No college name is used.
        No OUCE-specific priority is used.
        """

        if data.empty:
            return data

        student_rank = float(student_rank)

        # ------------------------------------------------------
        # Calculate cutoff gap
        # ------------------------------------------------------
        #
        # Example:
        #
        # Student rank = 3000
        #
        # Cutoff = 3100
        # gap = +100
        #
        # Cutoff = 2900
        # gap = -100
        #
        # ------------------------------------------------------

        data["cutoff_gap"] = (
            data["predicted_cutoff"]
            - student_rank
        )

        # ------------------------------------------------------
        # Absolute distance from student's rank
        # ------------------------------------------------------

        data["cutoff_distance"] = (
            data["cutoff_gap"].abs()
        )

        # ------------------------------------------------------
        # Recommendation group
        #
        # 0 = Realistic
        # 1 = Reach
        # ------------------------------------------------------

        data["recommendation_group"] = (
            data["cutoff_gap"] < 0
        ).astype(int)

        # ------------------------------------------------------
        # Evidence priority
        # ------------------------------------------------------

        evidence_order = {
            "Strong": 0,
            "Limited": 1,
            "Insufficient": 2
        }

        data["_evidence_order"] = (
            data["evidence_level"]
            .map(evidence_order)
            .fillna(2)
        )

        # ------------------------------------------------------
        # Final sorting
        #
        # IMPORTANT:
        #
        # We DO NOT sort by:
        #
        #     chance_level
        #
        # because that would put extremely easy colleges
        # before colleges whose cutoffs are actually close
        # to the student's rank.
        #
        # ------------------------------------------------------

        data = (
            data
            .sort_values(
                [
                    "recommendation_group",
                    "cutoff_distance",
                    "_evidence_order",
                    "predicted_cutoff"
                ],
                ascending=[
                    True,
                    True,
                    True,
                    True
                ],
                kind="mergesort"
            )
            .drop(
                columns=[
                    "recommendation_group",
                    "_evidence_order"
                ]
            )
            .reset_index(drop=True)
        )

        return data

    # ==========================================================
    # PREDICT
    # ==========================================================

    def predict(
        self,
        student_rank,
        category
    ):

        # ------------------------------------------------------
        # Validation
        # ------------------------------------------------------

        if student_rank is None:
            raise ValueError(
                "student_rank is required."
            )

        if student_rank <= 0:
            raise ValueError(
                "student_rank must be greater than 0."
            )

        if not category:
            raise ValueError(
                "category is required."
            )

        category = (
            str(category)
            .strip()
            .upper()
        )

        # ------------------------------------------------------
        # Get forecasts
        # ------------------------------------------------------

        data = self.forecast_cutoffs()

        # ------------------------------------------------------
        # Filter category
        # ------------------------------------------------------

        data = data[
            data["category"]
            .astype(str)
            .str.strip()
            .str.upper()
            == category
        ].copy()

        # ------------------------------------------------------
        # Remove unavailable predictions
        # ------------------------------------------------------

        data = data[
            data["predicted_cutoff"].notna()
        ].copy()

        data["predicted_cutoff"] = pd.to_numeric(
            data["predicted_cutoff"],
            errors="coerce"
        )

        data = data[
            data["predicted_cutoff"] > 0
        ].copy()

        if data.empty:
            return data

        # ------------------------------------------------------
        # Rank ratio
        # ------------------------------------------------------

        data["rank_ratio"] = (
            float(student_rank)
            /
            data["predicted_cutoff"]
        )

        # ------------------------------------------------------
        # Rank margin
        #
        # Positive:
        # predicted cutoff is greater than student's rank.
        #
        # Negative:
        # predicted cutoff is smaller than student's rank.
        # ------------------------------------------------------

        data["rank_margin"] = (
            data["predicted_cutoff"]
            -
            float(student_rank)
        )

        # ------------------------------------------------------
        # Chance classification
        # ------------------------------------------------------

        data["chance_level"] = (
            data["rank_ratio"]
            .apply(
                self.classify_chance
            )
        )

        # ------------------------------------------------------
        # FINAL CUTOFF-BASED ORDERING
        # ------------------------------------------------------

        data = self._sort_recommendations(
            data,
            student_rank
        )

        return data

    # ==========================================================
    # PREDICT CHANCE
    # ==========================================================

    def predict_chance(
        self,
        student_rank,
        category
    ):

        return self.predict(
            student_rank,
            category
        )

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    def recommendations(
        self,
        student_rank,
        category,
        limit=None,
        branches=None,
        districts=None,
        college_types=None
    ):
        """
        Return personalized college recommendations.

        Ranking is based entirely on historical cutoff fit.

        Realistic options are shown before reach options.

        Within each group, the predicted cutoff closest
        to the student's rank is shown first.

        No prestige ranking is used.
        """

        # ------------------------------------------------------
        # Get predictions
        # ------------------------------------------------------

        result = self.predict(
            student_rank,
            category
        ).copy()

        if result.empty:
            return result

        # ------------------------------------------------------
        # Normalize branch filters
        # ------------------------------------------------------

        if branches:

            branches = {
                str(x)
                .strip()
                .upper()
                for x in branches
            }

            result = result[
                result["branchCode"]
                .astype(str)
                .str.strip()
                .str.upper()
                .isin(branches)
            ].copy()

        if result.empty:
            return result

        # ------------------------------------------------------
        # College metadata
        # ------------------------------------------------------

        college_columns = [
            "collegeCode",
            "collegeName",
            "place",
            "district",
            "coEducation",
            "collegeType",
            "yearEstablished",
            "tuitionFee",
            "affiliatedTo"
        ]

        colleges = (
            self.colleges[
                college_columns
            ]
            .drop_duplicates(
                subset=[
                    "collegeCode"
                ]
            )
        )

        result = result.merge(
            colleges,
            on="collegeCode",
            how="left"
        )

        # ------------------------------------------------------
        # District filter
        # ------------------------------------------------------

        if districts:

            districts = {
                str(x)
                .strip()
                .upper()
                for x in districts
            }

            result = result[
                result["district"]
                .astype(str)
                .str.strip()
                .str.upper()
                .isin(districts)
            ].copy()

        if result.empty:
            return result

        # ------------------------------------------------------
        # College type filter
        # ------------------------------------------------------

        if college_types:

            college_types = {
                str(x)
                .strip()
                .upper()
                for x in college_types
            }

            result = result[
                result["collegeType"]
                .astype(str)
                .str.strip()
                .str.upper()
                .isin(college_types)
            ].copy()

        if result.empty:
            return result

        # ------------------------------------------------------
        # Branch metadata
        #
        # branchCode is not globally unique.
        #
        # Therefore use:
        #
        # collegeCode + branchCode
        # ------------------------------------------------------

        branch_columns = [
            "collegeCode",
            "branchCode",
            "branchName"
        ]

        branches_data = (
            self.branches[
                branch_columns
            ]
            .drop_duplicates(
                subset=[
                    "collegeCode",
                    "branchCode"
                ]
            )
        )

        result = result.merge(
            branches_data,
            on=[
                "collegeCode",
                "branchCode"
            ],
            how="left"
        )

        # ------------------------------------------------------
        # Clean college names
        # ------------------------------------------------------

        result["collegeName"] = (
            result["collegeName"]
            .astype("string")
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
            .str.strip()
        )

        # ------------------------------------------------------
        # Clean branch names
        # ------------------------------------------------------

        result["branchName"] = (
            result["branchName"]
            .astype("string")
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
            .str.strip()
        )

        # ------------------------------------------------------
        # Re-apply recommendation ordering after filters.
        #
        # Filtering must NOT change the recommendation logic.
        # ------------------------------------------------------

        result = self._sort_recommendations(
            result,
            student_rank
        )

        # ------------------------------------------------------
        # Limit results
        # ------------------------------------------------------

        if limit is not None:

            if limit <= 0:
                return result.iloc[
                    0:0
                ].copy()

            result = result.head(
                int(limit)
            )

        return result.reset_index(
            drop=True
        )

    # ==========================================================
    # BACKTEST DATA
    # ==========================================================

    def backtest_data(self):

        data = self.final_cutoffs()

        # Training period

        train = data[
            data["year"].isin(
                [2023, 2024]
            )
        ].copy()

        # Holdout period

        test = data[
            data["year"] == 2025
        ].copy()

        return train, test

    # ==========================================================
    # BACKTEST FORECAST
    # ==========================================================

    def backtest_forecast(self):

        train, test = self.backtest_data()

        keys = [
            "collegeCode",
            "branchCode",
            "category"
        ]

        # ------------------------------------------------------
        # Historical years available
        # ------------------------------------------------------

        history = (
            train
            .groupby(keys)
            .agg(
                years_available=(
                    "year",
                    "nunique"
                )
            )
            .reset_index()
        )

        # ------------------------------------------------------
        # Convert training data to year columns
        # ------------------------------------------------------

        pivot = (
            train
            .pivot_table(
                index=keys,
                columns="year",
                values="closingRank",
                aggfunc="mean"
            )
            .reset_index()
        )

        if 2023 not in pivot.columns:
            pivot[2023] = pd.NA

        if 2024 not in pivot.columns:
            pivot[2024] = pd.NA

        # ------------------------------------------------------
        # Same forecasting logic as production
        # ------------------------------------------------------

        pivot["predicted_cutoff"] = pd.NA

        both = (
            pivot[2023].notna() &
            pivot[2024].notna()
        )

        pivot.loc[
            both,
            "predicted_cutoff"
        ] = (
            pivot.loc[both, 2023] * 0.7
            +
            pivot.loc[both, 2024] * 0.3
        )

        only_2023 = (
            pivot[2023].notna() &
            pivot[2024].isna()
        )

        pivot.loc[
            only_2023,
            "predicted_cutoff"
        ] = pivot.loc[
            only_2023,
            2023
        ]

        only_2024 = (
            pivot[2023].isna() &
            pivot[2024].notna()
        )

        pivot.loc[
            only_2024,
            "predicted_cutoff"
        ] = pivot.loc[
            only_2024,
            2024
        ]

        # ------------------------------------------------------
        # Merge with 2025 actual results
        # ------------------------------------------------------

        predictions = pivot[
            keys + [
                "predicted_cutoff"
            ]
        ].copy()

        predictions = predictions[
            predictions[
                "predicted_cutoff"
            ].notna()
        ].copy()

        result = test.merge(
            predictions,
            on=keys,
            how="inner"
        )

        # ------------------------------------------------------
        # Evidence
        # ------------------------------------------------------

        result = result.merge(
            history,
            on=keys,
            how="left"
        )

        result["evidence_level"] = (
            result["years_available"]
            .apply(
                lambda x:
                "Strong"
                if x >= 2
                else
                "Limited"
                if x == 1
                else
                "Insufficient"
            )
        )

        # ------------------------------------------------------
        # Prediction error
        # ------------------------------------------------------

        result["error"] = (
            result["closingRank"]
            -
            result["predicted_cutoff"]
        )

        result["absolute_error"] = (
            result["error"].abs()
        )

        # ------------------------------------------------------
        # Error percentage
        # ------------------------------------------------------

        result["error_pct"] = (
            result["error"]
            /
            result["predicted_cutoff"]
            * 100
        )

        result["absolute_error_pct"] = (
            result["error_pct"].abs()
        )

        # ------------------------------------------------------
        # Actual / predicted ratio
        # ------------------------------------------------------

        result["actual_ratio"] = (
            result["closingRank"]
            /
            result["predicted_cutoff"]
        )

        return result

    # ==========================================================
    # HISTORICAL SUCCESS CALIBRATION
    # ==========================================================

    def calibration(self):

        backtest = self.backtest_forecast()

        ratios = [
            0.50,
            0.60,
            0.70,
            0.75,
            0.80,
            0.85,
            0.90,
            0.95,
            1.00,
            1.05,
            1.10,
            1.20
        ]

        rows = []

        for ratio in ratios:

            success_rate = (
                (
                    backtest[
                        "actual_ratio"
                    ]
                    >= ratio
                ).mean()
                * 100
            )

            rows.append(
                {
                    "student_ratio": ratio,
                    "success_rate": success_rate
                }
            )

        return pd.DataFrame(rows)