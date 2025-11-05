# 🚀 Complete Setup and Run Guide

This guide will help you set up and run the entire Web Sémantique Platform project.

## 📋 Prerequisites

Before starting, ensure you have:

- **Java** (JDK 8 or higher) - Required for Fuseki
- **Python 3.8+** - For backend
- **Node.js 16+** and **npm** - For frontend
- **Git** - (if cloning the repository)

## 🔧 Step-by-Step Setup

### **Step 1: Install Python Dependencies**

```powershell
# Navigate to backend directory
cd backend

# Install Python packages
pip install -r requirements.txt
```

**Required packages:**
- Flask, Flask-CORS
- SPARQLWrapper
- RDFLib
- google-generativeai (Gemini AI)
- python-dotenv
- requests

### **Step 2: Install Frontend Dependencies**

```powershell
# Navigate to frontend directory
cd frontend

# Install Node.js packages
npm install
```

### **Step 3: Configure Environment Variables**

Create a `.env` file in the `backend/` directory:

```bash
# Backend/.env

# Fuseki Configuration (optional - defaults shown)
FUSEKI_ENDPOINT=http://localhost:3030/educationInfin

# Google Gemini API Key (REQUIRED for semantic search)
GEMINI_API_KEY=your_gemini_api_key_here

# TALN API Configuration (OPTIONAL - has fallback)
TALN_API_KEY=your_taln_api_key_here
TALN_API_URL=https://api.taln.fr/v1
```

**Getting a Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste it in your `.env` file

**Note:** TALN API is optional - the system has a built-in fallback that works without it.

### **Step 4: Start Fuseki Server**

Fuseki is the SPARQL server that stores your RDF/OWL data.

**On Windows (PowerShell):**
```powershell
cd fuseki/apache-jena-fuseki-5.6.0
java -jar fuseki-server.jar
```

**On Linux/Mac:**
```bash
cd fuseki/apache-jena-fuseki-5.6.0
./fuseki-server
```

**Or use the batch file (Windows):**
```powershell
cd fuseki/apache-jena-fuseki-5.6.0
.\fuseki-server.bat
```

**Verify Fuseki is running:**
- Open browser: http://localhost:3030
- You should see the Fuseki web interface
- Two datasets should be visible: `educationInfin` and `eco-ontology`

**Keep this terminal open!** Fuseki must stay running.

### **Step 5: Load Data into Fuseki**

In a **new terminal window**, load the education ontology data:

```powershell
# Navigate to scripts directory
cd scripts

# Run the data loader
python load_data.py
```

**What this does:**
- Connects to Fuseki
- Clears existing data (optional)
- Loads `data/educationInfin.rdf` into the `educationInfin` dataset
- Verifies the data was loaded successfully

**Expected output:**
```
✓ Connexion à Fuseki réussie
✓ Dataset vidé avec succès
✓ Ontologie chargée: XXXX triplets trouvés
✓ Données chargées avec succès
✓ Total des triplets dans Fuseki: XXXX
🎉 CHARGEMENT TERMINÉ AVEC SUCCÈS!
```

### **Step 6: Start Backend Server**

In a **new terminal window**:

```powershell
# Navigate to backend directory
cd backend

# Start Flask server
python app.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

**Verify backend is running:**
- Open browser: http://localhost:5000
- Should see: `{"message": "Education Intelligente Platform API is running!"}`
- Test endpoint: http://localhost:5000/api/health

**Keep this terminal open!** Backend must stay running.

### **Step 7: Start Frontend Application**

In a **new terminal window**:

```powershell
# Navigate to frontend directory
cd frontend

# Start React development server
npm start
```

**Expected output:**
```
Compiled successfully!
You can now view frontend in the browser.
  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

The browser should automatically open to http://localhost:3000

**Keep this terminal open!** Frontend must stay running.

## ✅ Verification Checklist

After starting all services, verify everything works:

### **1. Fuseki (http://localhost:3030)**
- ✅ Web interface loads
- ✅ `educationInfin` dataset visible
- ✅ `eco-ontology` dataset visible

### **2. Backend (http://localhost:5000)**
- ✅ Home page shows: `{"message": "Education Intelligente Platform API is running!"}`
- ✅ Health check: http://localhost:5000/api/health
- ✅ Test connection: http://localhost:5000/api/test (should show data counts)

### **3. Frontend (http://localhost:3000)**
- ✅ React app loads
- ✅ Navigation bar visible
- ✅ Semantic Search page loads
- ✅ Can navigate to different pages (Personnes, Universites, etc.)

### **4. Semantic Search Test**
1. Go to http://localhost:3000 (Semantic Search page)
2. Type a question: "Tous les événements"
3. Click "Rechercher"
4. Should see:
   - TALN analysis results
   - Generated SPARQL query
   - Query results

## 🎯 Quick Start Commands Summary

**Terminal 1 - Fuseki:**
```powershell
cd fuseki/apache-jena-fuseki-5.6.0
java -jar fuseki-server.jar
```

**Terminal 2 - Load Data (one-time):**
```powershell
cd scripts
python load_data.py
```

**Terminal 3 - Backend:**
```powershell
cd backend
python app.py
```

**Terminal 4 - Frontend:**
```powershell
cd frontend
npm start
```

## 🔍 Troubleshooting

### **Problem: Fuseki won't start**
- **Check:** Is Java installed? Run `java -version`
- **Check:** Is port 3030 available? Try a different port in Fuseki config
- **Solution:** Make sure no other application is using port 3030

### **Problem: Backend can't connect to Fuseki**
- **Check:** Is Fuseki running? Visit http://localhost:3030
- **Check:** Is the dataset name correct? Should be `educationInfin`
- **Solution:** Verify `FUSEKI_ENDPOINT` in `.env` matches your Fuseki setup

### **Problem: Frontend can't connect to backend**
- **Check:** Is backend running? Visit http://localhost:5000
- **Check:** CORS errors in browser console
- **Solution:** Backend has CORS enabled, but verify it's running on port 5000

### **Problem: Semantic search returns errors**
- **Check:** Is `GEMINI_API_KEY` set in `.env`?
- **Check:** Backend logs for error messages
- **Solution:** The system has fallback queries, but Gemini API key is recommended

### **Problem: No data in frontend**
- **Check:** Was data loaded? Run `python scripts/load_data.py` again
- **Check:** Backend `/api/test` endpoint shows data counts
- **Solution:** Verify data file exists: `data/educationInfin.rdf`

### **Problem: Port already in use**
- **Fuseki (3030):** Change port in Fuseki configuration or stop other service
- **Backend (5000):** Change port in `app.py` or use `python app.py --port 5001`
- **Frontend (3000):** React will ask to use a different port automatically

## 📊 Service Ports Reference

| Service | Port | URL |
|---------|------|-----|
| Fuseki | 3030 | http://localhost:3030 |
| Backend API | 5000 | http://localhost:5000 |
| Frontend | 3000 | http://localhost:3000 |

## 🔄 Running Order (Important!)

**Start services in this order:**

1. **Fuseki** (must be first - data storage)
2. **Load Data** (one-time, after Fuseki starts)
3. **Backend** (depends on Fuseki)
4. **Frontend** (depends on Backend)

**Stop services in reverse order:**

1. Frontend (Ctrl+C)
2. Backend (Ctrl+C)
3. Fuseki (Ctrl+C)

## 🎓 What Each Service Does

### **Fuseki (Port 3030)**
- SPARQL server storing RDF/OWL data
- Provides query endpoints for semantic data
- Web interface for data management

### **Backend (Port 5000)**
- Flask API server
- Processes SPARQL queries
- Integrates with Gemini AI for semantic search
- Provides RESTful endpoints for all entities

### **Frontend (Port 3000)**
- React web application
- User interface for browsing and searching data
- Semantic search interface
- CRUD operations for entities

## 🚀 Production Deployment

For production, consider:
- Using a process manager (PM2, Supervisor) for backend
- Building frontend: `npm run build`
- Using a production WSGI server (Gunicorn) for Flask
- Setting up proper security (HTTPS, authentication)
- Using persistent storage for Fuseki (TDB instead of in-memory)

## 📝 Notes

- **Fuseki datasets:** Already configured in `fuseki/apache-jena-fuseki-5.6.0/run/configuration/`
- **Default dataset:** `educationInfin` (can be changed in `.env`)
- **Data persistence:** Fuseki uses in-memory storage by default (data resets on restart)
- **For persistence:** Modify Fuseki config to use TDB (see Fuseki documentation)

---

**Need help?** Check the logs in each terminal window for error messages.

