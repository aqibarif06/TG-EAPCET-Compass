import { useEffect, useState } from "react";
import axios from "axios";
import {
  Search,
  GraduationCap,
  MapPin,
  Building2,
  SlidersHorizontal,
  ArrowRight,
  Loader2,
  Moon,
  Sun,
} from "lucide-react";
import "./App.css";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";
function App() {
  const [darkMode, setDarkMode] = useState(false);

  const [rank, setRank] = useState("");
  const [category, setCategory] = useState("OC_BOYS");

  const [branches, setBranches] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [collegeTypes, setCollegeTypes] = useState([]);
  const [categories, setCategories] = useState([]);

  const [selectedBranches, setSelectedBranches] = useState([]);
  const [selectedDistricts, setSelectedDistricts] = useState([]);
  const [selectedCollegeTypes, setSelectedCollegeTypes] =
    useState([]);

  const [results, setResults] = useState([]);

  const [loadingOptions, setLoadingOptions] = useState(true);
  const [loadingResults, setLoadingResults] = useState(false);
  const [error, setError] = useState("");

  // ==========================================================
  // LOAD FILTER OPTIONS
  // ==========================================================

  useEffect(() => {
    async function loadOptions() {
      try {
        const [
          categoryRes,
          branchRes,
          districtRes,
          typeRes,
        ] = await Promise.all([
          axios.get(`${API_BASE_URL}/api/categories`),
          axios.get(`${API_BASE_URL}/api/branches`),
          axios.get(`${API_BASE_URL}/api/districts`),
          axios.get(`${API_BASE_URL}/api/college-types`),
        ]);

        setCategories(
          categoryRes.data.categories || []
        );

        // Keep only unique branch codes.
        const uniqueBranches = (
          branchRes.data.branches || []
        )
          .filter(
            (item) =>
              item.branchCode &&
              item.branchName
          )
          .filter(
            (item, index, array) =>
              index ===
              array.findIndex(
                (branch) =>
                  branch.branchCode ===
                  item.branchCode
              )
          )
          .sort((a, b) =>
            a.branchCode.localeCompare(
              b.branchCode
            )
          );

        setBranches(uniqueBranches);

        setDistricts(
          districtRes.data.districts || []
        );

        setCollegeTypes(
          typeRes.data.collegeTypes || []
        );

        if (
          categoryRes.data.categories?.length
        ) {
          if (
            categoryRes.data.categories.includes(
              "OC_BOYS"
            )
          ) {
            setCategory("OC_BOYS");
          } else {
            setCategory(
              categoryRes.data.categories[0]
            );
          }
        }
      } catch (err) {
        console.error(err);

        setError(
          "Unable to connect to the TG-EAPCET Compass backend. Make sure FastAPI is running on port 8000."
        );
      } finally {
        setLoadingOptions(false);
      }
    }

    loadOptions();
  }, []);

  // ==========================================================
  // TOGGLE FILTER
  // ==========================================================

  function toggleValue(value, setter) {
    setter((current) =>
      current.includes(value)
        ? current.filter(
            (item) => item !== value
          )
        : [...current, value]
    );
  }

  // ==========================================================
  // PREDICTION
  // ==========================================================

  async function handlePredict(event) {
    event.preventDefault();

    if (!rank || Number(rank) <= 0) {
      setError(
        "Please enter a valid EAPCET rank."
      );
      return;
    }

    setError("");
    setLoadingResults(true);
    setResults([]);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/predict`,
        {
          rank: Number(rank),
          category,

          branches:
            selectedBranches.length > 0
              ? selectedBranches
              : null,

          districts:
            selectedDistricts.length > 0
              ? selectedDistricts
              : null,

          collegeTypes:
            selectedCollegeTypes.length > 0
              ? selectedCollegeTypes
              : null,

          limit: 20,
        }
      );

      setResults(
        response.data.results || []
      );
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Prediction failed. Please make sure the backend is running."
      );
    } finally {
      setLoadingResults(false);
    }
  }

  // ==========================================================
  // FORMAT NUMBER
  // ==========================================================

  function formatNumber(value) {
    if (
      value === null ||
      value === undefined ||
      Number.isNaN(Number(value))
    ) {
      return "—";
    }

    return Number(value).toLocaleString(
      "en-IN",
      {
        maximumFractionDigits: 0,
      }
    );
  }

  // ==========================================================
  // CHANCE CLASS
  // ==========================================================

  function chanceClass(chance) {
    return (
      chance
        ?.toLowerCase()
        .replace(/\s+/g, "-") || ""
    );
  }

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <div
      className={
        darkMode
          ? "app dark-mode"
          : "app"
      }
    >
      {/* ================================================== */}
      {/* NAVBAR */}
      {/* ================================================== */}

      <header className="navbar">
        <div className="brand">
          <div>
            <h1>TG-EAPCET Compass</h1>
            <span>College Predictor</span>
          </div>
        </div>

        <div className="navbar-right">
          <div className="status">
            <span className="status-dot"></span>
            Predictor Online
          </div>

          <button
            type="button"
            className="theme-toggle"
            onClick={() =>
              setDarkMode(
                (current) => !current
              )
            }
            aria-label={
              darkMode
                ? "Switch to light mode"
                : "Switch to dark mode"
            }
            title={
              darkMode
                ? "Switch to light mode"
                : "Switch to dark mode"
            }
          >
            {darkMode ? (
              <Sun size={18} />
            ) : (
              <Moon size={18} />
            )}
          </button>
        </div>
      </header>

      {/* ================================================== */}
      {/* MAIN */}
      {/* ================================================== */}

      <main>
        {/* ================================================== */}
        {/* HERO */}
        {/* ================================================== */}

        <section className="hero">
          <div className="hero-content">
            <span className="eyebrow">
              DATA-DRIVEN COLLEGE PREDICTION
            </span>

            <h2>
              Find the colleges
              <br />
              <span>within your reach.</span>
            </h2>

            <p>
              Enter your TG EAPCET rank and
              preferences. Compass analyzes
              historical cutoff data to help you
              discover suitable colleges and
              branches.
            </p>

            <div className="hero-stats">
              <div>
                <strong>46K+</strong>
                <span>
                  Historical cutoff records
                </span>
              </div>

              <div>
                <strong>169</strong>
                <span>Colleges</span>
              </div>

              <div>
                <strong>42</strong>
                <span>Branch codes</span>
              </div>
            </div>
          </div>

          <div className="hero-visual">
            <div className="compass-circle">
              <div className="compass-inner">
                <GraduationCap size={54} />
                <span>COMPASS</span>
              </div>

              <div className="compass-point point-top">
                N
              </div>

              <div className="compass-point point-right">
                E
              </div>

              <div className="compass-point point-bottom">
                S
              </div>

              <div className="compass-point point-left">
                W
              </div>
            </div>
          </div>
        </section>

        {/* ================================================== */}
        {/* PREDICTOR */}
        {/* ================================================== */}

        <section className="predictor-section">
          <div className="section-heading">
            <div>
              <span className="section-label">
                01 — YOUR PROFILE
              </span>

              <h3>
                Tell us about your rank
              </h3>
            </div>

            <SlidersHorizontal size={22} />
          </div>

          {error && (
            <div className="error-box">
              {error}
            </div>
          )}

          <form onSubmit={handlePredict}>
            <div className="form-grid">
              {/* RANK */}

              <div className="field field-large">
                <label>
                  <Search size={17} />
                  EAPCET Rank
                </label>

                <input
                  type="number"
                  min="1"
                  value={rank}
                  onChange={(e) =>
                    setRank(e.target.value)
                  }
                  placeholder="e.g. 25000"
                />

                <small>
                  Enter your overall TG EAPCET
                  rank
                </small>
              </div>

              {/* CATEGORY */}

              <div className="field">
                <label>
                  <GraduationCap size={17} />
                  Category
                </label>

                <select
                  value={category}
                  onChange={(e) =>
                    setCategory(
                      e.target.value
                    )
                  }
                  disabled={loadingOptions}
                >
                  {categories.length === 0 ? (
                    <option value="OC_BOYS">
                      OC_BOYS
                    </option>
                  ) : (
                    categories.map(
                      (item) => (
                        <option
                          key={item}
                          value={item}
                        >
                          {item}
                        </option>
                      )
                    )
                  )}
                </select>
              </div>
            </div>

            {/* ================================================== */}
            {/* FILTERS */}
            {/* ================================================== */}

            <div className="filters">
              {/* BRANCHES */}

              <div className="filter-group">
                <label>
                  Branches
                  <span className="filter-count">
                    {branches.length}
                  </span>
                </label>

                <div className="chips">
                  {branches.map(
                    (item) => {
                      const code =
                        item.branchCode;

                      return (
                        <button
                          type="button"
                          key={code}
                          title={
                            item.branchName
                          }
                          className={
                            selectedBranches.includes(
                              code
                            )
                              ? "chip active"
                              : "chip"
                          }
                          onClick={() =>
                            toggleValue(
                              code,
                              setSelectedBranches
                            )
                          }
                        >
                          {code}
                        </button>
                      );
                    }
                  )}
                </div>
              </div>

              {/* DISTRICTS */}

              <div className="filter-group">
                <label>
                  Districts
                  <span className="filter-count">
                    {districts.length}
                  </span>
                </label>

                <div className="chips">
                  {districts.map(
                    (district) => (
                      <button
                        type="button"
                        key={district}
                        className={
                          selectedDistricts.includes(
                            district
                          )
                            ? "chip active"
                            : "chip"
                        }
                        onClick={() =>
                          toggleValue(
                            district,
                            setSelectedDistricts
                          )
                        }
                      >
                        {district}
                      </button>
                    )
                  )}
                </div>
              </div>

              {/* COLLEGE TYPES */}

              <div className="filter-group">
                <label>
                  College Type
                  <span className="filter-count">
                    {collegeTypes.length}
                  </span>
                </label>

                <div className="chips">
                  {collegeTypes.map(
                    (type) => (
                      <button
                        type="button"
                        key={type}
                        className={
                          selectedCollegeTypes.includes(
                            type
                          )
                            ? "chip active"
                            : "chip"
                        }
                        onClick={() =>
                          toggleValue(
                            type,
                            setSelectedCollegeTypes
                          )
                        }
                      >
                        {type}
                      </button>
                    )
                  )}
                </div>
              </div>
            </div>

            {/* SUBMIT */}

            <button
              className="predict-button"
              type="submit"
              disabled={loadingResults}
            >
              {loadingResults ? (
                <>
                  <Loader2
                    className="spin"
                    size={20}
                  />
                  Analyzing...
                </>
              ) : (
                <>
                  Find My Colleges
                  <ArrowRight size={20} />
                </>
              )}
            </button>
          </form>
        </section>

        {/* ================================================== */}
        {/* RESULTS */}
        {/* ================================================== */}

        {results.length > 0 && (
          <section className="results-section">
            <div className="section-heading">
              <div>
                <span className="section-label">
                  02 — RECOMMENDATIONS
                </span>

                <h3>
                  Colleges you can target
                </h3>
              </div>

              <span className="result-count">
                {results.length} results
              </span>
            </div>

            <div className="results-grid">
              {results.map(
                (college, index) => (
                  <article
                    className="result-card"
                    key={`${college.collegeCode}-${college.branchCode}-${index}`}
                  >
                    <div className="card-top">
                      <span className="rank-number">
                        #{index + 1}
                      </span>

                      <span
                        className={`chance ${chanceClass(
                          college.chance_level
                        )}`}
                      >
                        {
                          college.chance_level
                        }
                      </span>
                    </div>

                    <h4>
                      {college.collegeName ||
                        college.collegeCode}
                    </h4>

                    <p className="branch-name">
                      {college.branchName ||
                        college.branchCode}
                    </p>

                    <div className="location">
                      <MapPin size={15} />

                      {college.place ||
                        "—"}
                      ,{" "}
                      {college.district ||
                        "—"}
                    </div>

                    <div className="card-stats">
                      <div>
                        <span>
                          Predicted cutoff
                        </span>

                        <strong>
                          {formatNumber(
                            college.predicted_cutoff
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Your margin
                        </span>

                        <strong>
                          {formatNumber(
                            college.rank_margin
                          )}
                        </strong>
                      </div>
                    </div>

                    <div className="card-footer">
                      <span>
                        <Building2
                          size={14}
                        />

                        {
                          college.collegeType
                        }
                      </span>

                      <span
                        className={`evidence ${college.evidence_level?.toLowerCase()}`}
                      >
                        {
                          college.evidence_level
                        }{" "}
                        evidence
                      </span>
                    </div>
                  </article>
                )
              )}
            </div>
          </section>
        )}

        {/* ================================================== */}
        {/* EMPTY STATE */}
        {/* ================================================== */}

        {!loadingResults &&
          results.length === 0 &&
          rank && (
            <div className="empty-state">
              Submit your profile to see
              college recommendations.
            </div>
          )}
      </main>

      {/* ================================================== */}
      {/* FOOTER */}
      {/* ================================================== */}

      <footer>
        <span>
          TG-EAPCET Compass
        </span>

        <span>
          Predictions are based on historical
          cutoff data and should be used as
          guidance, not a guarantee.
        </span>
      </footer>
    </div>
  );
}

export default App;