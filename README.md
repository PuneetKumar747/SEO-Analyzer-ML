# **SEO Rank Predictor - Flask Web App** 🚀  

## **Overview**  
This project is a **Flask-based web application** that predicts the ranking of a website based on various SEO factors such as **title importance, headers, body text, meta tags, alt text for images, loading speed, and backlinks**. It uses **Machine Learning (ML)** to make predictions and stores data in a **PostgreSQL database**. The app also supports **Google OAuth authentication** for user login.  

---

## **Features**  
✅ **User Authentication:** Sign-up, login, and Google OAuth integration.  
✅ **SEO Analysis:** Extracts key SEO elements from a given URL and evaluates their importance.  
✅ **Machine Learning-Based Ranking:** Uses a trained **ML model (Joblib)** for rank prediction.  
✅ **Database Storage:** PostgreSQL integration to store user and website ranking data.  
✅ **Admin Panel:** Secure admin login to view SEO analysis history.  
✅ **Web Scraping:** Uses **BeautifulSoup** to fetch and analyze website content.  
✅ **Page Speed Insights:** Retrieves website loading speed using Google's API.  

---

## **Tech Stack**  
- **Backend:** Flask (Python)  
- **Frontend:** HTML, CSS, Jinja Templates  
- **Database:** PostgreSQL  
- **Machine Learning:** Scikit-Learn, Joblib, NumPy  
- **Authentication:** Google OAuth (Authlib)  
- **Web Scraping:** BeautifulSoup, Requests  
- **Deployment:** Flask Server (localhost)  

---

## **Installation & Setup**  
1️⃣ Clone the repository:  
```bash
git clone https://github.com/PuneetKumar747/SEO-Analyzer-ML.git
cd SEO-Analyzer-ML
git clone https://github.com/your-username/your-repo.git
cd your-repo
```
2️⃣ Install dependencies:  
```bash
pip install -r requirements.txt
```
3️⃣ Set up PostgreSQL and create the required tables (defined in `app.py`).  

4️⃣ Run the Flask app:  
```bash
python app.py
```
5️⃣ Access the web app at:  
```bash
http://127.0.0.1:5000
```

---

## **Usage**  
🔹 **Sign up/Login** using Google OAuth or email.  
🔹 Enter a **website URL** and a **search query** to analyze SEO performance.  
🔹 The system will **predict** the website's ranking based on its **SEO factors**.  
🔹 **Admins** can log in to view **past analysis history**.  

---

## **Contributing**  
Feel free to **fork the repository** and submit **pull requests** if you want to improve the project!  

---
