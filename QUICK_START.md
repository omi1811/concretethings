# ⚡ Quick Start - ConcreteThings

## 🎯 For Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Migrate database (adds image support)
python migrate_db.py

# 3. Seed sample data (optional)
python seed.py

# 4. Start server
python -m server.app

# 5. Open http://localhost:8000
```

**Test it:** Upload an image when creating a mix design!

---

## 🚀 For Production Deployment

### **Easiest: Heroku (5 minutes)**
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
git push heroku main
heroku run python migrate_db.py
heroku open
```

### **Best Value: Railway ($5/month)**
```bash
railway init
railway up
# Add PostgreSQL plugin in dashboard
# Set environment variables
```

### **Most Control: Docker**
```bash
docker-compose up -d
# Edit docker-compose.yml for production settings
```

📖 **Full guide:** [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 💾 Recommended Databases

| Use Case | Database | Cost | Why? |
|----------|----------|------|------|
| **Development** | SQLite | Free | Built-in, zero config |
| **Small Business** | Supabase | Free-$25 | Easy, managed, includes storage |
| **Medium Business** | DigitalOcean PG | $15 | Reliable, simple pricing |
| **Enterprise** | AWS RDS | $50+ | Scalable, enterprise support |

---

## 📸 New Image Features

✅ Upload images with mix designs  
✅ Automatic compression & optimization  
✅ Thumbnails in table view  
✅ Click for fullscreen preview  
✅ Stored in database (no filesystem clutter)  

---

## 🔗 Key Files

- `README.md` - Overview & quick start
- `DEPLOYMENT.md` - Full deployment guide (45 pages)
- `COMMERCIAL_READY.md` - Business features
- `COMPLETE_SUMMARY.md` - Everything delivered
- `server/app.py` - Main application code
- `.env` - Configuration (copy from .env.example)

---

## 💡 Common Commands

```bash
# Development server
python -m server.app

# Production server (Gunicorn)
gunicorn --config gunicorn.conf.py 'server.app:create_app()'

# Test database
python test_db.py

# Test API (server must be running)
python test_api.py

# Migrate database
python migrate_db.py

# Reset database
rm data.sqlite3
python -c "from server.db import init_db; init_db()"
python seed.py
```

---

## 🐛 Troubleshooting

**"Module not found"**
```bash
pip install -r requirements.txt
```

**"No such column: image_name"**
```bash
python migrate_db.py
```

**"Port already in use"**
```bash
pkill -f 'python.*server.app'
# or change PORT in .env
```

**"Database locked"**
```bash
# Switch to PostgreSQL for production
# SQLite doesn't handle concurrent writes well
```

---

## 📞 Get Help

1. Read the docs in this order:
   - README.md
   - DEPLOYMENT.md
   - Code comments

2. Check logs:
   - `server.log`
   - Terminal output

3. Test endpoints:
   - `python test_db.py`
   - `python test_api.py`

---

**Ready in 5 minutes! 🚀**
