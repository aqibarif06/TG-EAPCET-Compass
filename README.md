# TG-EAPCET Compass 🎓

A data-driven college prediction and recommendation system for **TG EAPCET** aspirants.

TG-EAPCET Compass analyzes historical cutoff data across colleges, branches, categories, districts, and college types to help students identify colleges and branches that are realistically within their rank range.

## 🌐 Live Demo

**Frontend:**
https://tg-eapcet-compass.vercel.app/

**Backend API:**
https://tg-eapcet-compass-api.onrender.com/

---

## 📌 Problem Statement

Choosing colleges after TG EAPCET can be difficult because students need to consider:

- Their EAPCET rank
- Reservation category
- Branch preference
- College type
- District preference
- Historical closing ranks

Simply listing colleges by reputation does not answer the most important question:

> **"Which colleges and branches am I realistically likely to get with my rank?"**

TG-EAPCET Compass addresses this by using historical cutoff data to estimate cutoff behavior and rank recommendations according to their proximity to the student's rank.

---

## ✨ Features

### 🎯 Rank-Based College Recommendations

Enter your TG EAPCET rank and category to receive college and branch recommendations based on historical cutoff data.

### 📊 Cutoff-Based Ranking

Recommendations are ranked primarily according to the relationship between:

- Student's rank
- Predicted historical cutoff
- Cutoff gap / distance

This means the system prioritizes colleges that are **closer to the student's actual rank**, rather than simply placing prestigious colleges at the top.

### 🏫 College & Branch Filtering

Students can filter recommendations by:

- Branch
- District
- College type

### 🧑‍🎓 Category Support

The predictor supports category-specific cutoff data, including categories such as:

- OC
- BC
- SC
- ST
- EWS
- Other available category/gender combinations in the dataset

### 📍 Geographic Filtering

Recommendations can be filtered by district to help students identify colleges in preferred locations.

### 🌙 Dark Mode

The frontend includes a responsive dark theme with a neon-inspired visual design.

### 📱 Responsive Interface

The application is designed to work across desktop and mobile screen sizes.

---

## 🧠 How the Prediction Works

TG-EAPCET Compass currently uses a **historical cutoff-based prediction approach**.

The system processes historical cutoff records and generates a predicted cutoff for each eligible college-branch combination.

The student's rank is then compared with the predicted cutoff.

### Example

Suppose a student has:

```text
Rank: 3000
Category: OC_BOYS


College A
Predicted cutoff: 2900

College B
Predicted cutoff: 3310

College C
Predicted cutoff: 5200

Student Rank
      ↓
Compare with Predicted Cutoff
      ↓
Calculate Cutoff Gap / Distance
      ↓
Classify Opportunity
      ↓
Rank Recommendations