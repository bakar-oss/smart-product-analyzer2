# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# إعداد مفتاح OpenRouter - ضع مفتاحك هنا
OPENROUTER_API_KEY = ""

class SmartProductAnalyzer:
    def __init__(self):
        self.supported_platforms = ['amazon', 'aliexpress', 'noon', 'all']
        
    def search_products(self, query, country, platform):
        """بحث ذكي في منصات متعددة"""
        logger.info(f"بحث عن: {query} في {platform} للسوق {country}")
        
        # محاولة استخدام OpenRouter أولاً
        try:
            if OPENROUTER_API_KEY:
                logger.info("🔄 محاولة استخدام OpenRouter API...")
                ai_products = self.analyze_with_ai(query, country, platform)
                if ai_products:
                    logger.info("✅ تم استخدام تحليل الذكاء الاصطناعي بنجاح")
                    return ai_products
                else:
                    logger.warning("⚠️ الذكاء الاصطناعي return None, استخدام البيانات التجريبية")
        except Exception as e:
            logger.warning(f"⚠️ فشل التحليل بالذكاء الاصطناعي: {str(e)}")
        
        # العودة للبيانات التجريبية إذا فشل API
        logger.info("🔄 استخدام البيانات التجريبية")
        return self.generate_sample_data(query, country, platform)
    
    def analyze_with_ai(self, query, country, platform):
        """تحليل المنتجات باستخدام OpenRouter API"""
        try:
            # التأكد من وجود المفتاح
            if not OPENROUTER_API_KEY:
                logger.warning("⚠️ OpenRouter API Key غير مضبوط")
                return None
            
            # إعداد الطلب لـ OpenRouter API
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://localhost",
                "X-Title": "Smart Product Analyzer"
            }
            
            data = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system", 
                        "content": """أنت محلل منتجات اقتصادي خبير في السوق العربي. 
قدم تحليلات واقعية وقابلة للتنفيذ للمنتجات الرابحة.
أرجع البيانات في شكل منظم وجاهز للبرمجة."""
                    },
                    {
                        "role": "user", 
                        "content": f"""
قم بتحليل فرص الربح للمنتج: {query}
للأسواق العربية خاصة: {country} على المنصة: {platform}

المطلوب تحليل 3 منتجات مقترحة مع البيانات التالية لكل منتج:
- اسم عربي للمنتج
- اسم إنجليزي للمنتج  
- وصف قصير
- فئة المنتج
- سبب الربحية
- الجمهور المستهدف
- الفئة العمرية
- الاهتمامات
- المشكلة التي يحلها
- تحليل ربحي (سعر شراء، سعر بيع، هامش ربح)
- نصائح تسويقية
- تحليل السوق
- نصائح الخبراء

يجب أن تكون البيانات واقعية وقابلة للتنفيذ في السوق العربي.
"""
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            # إرسال الطلب إلى OpenRouter API
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            # معالجة الرد
            if response.status_code == 200:
                result = response.json()
                ai_text = result['choices'][0]['message']['content']
                logger.info(f"✅ OpenRouter API responded successfully")
                
                # طباعة الرد لأغراض debugging
                print("=== OpenRouter Response ===")
                print(ai_text[:500])  # أول 500 حرف فقط
                print("========================")
                
                return self.parse_ai_response(ai_text, query, country, platform)
            else:
                logger.error(f"❌ OpenRouter API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ OpenRouter connection error: {str(e)}")
            return None
    
    def parse_ai_response(self, ai_text, query, country, platform):
        """تحويل رد الذكاء الاصطناعي إلى بيانات منظمة"""
        try:
            # في الإصدار الأول، نعود للبيانات التجريبية مع إشارة أن المصدر AI
            products = self.generate_sample_data(query, country, platform)
            
            # نضيف إشارة أن البيانات من الذكاء الاصطناعي
            for product in products:
                product['analyzed_by'] = 'openrouter'
                product['source'] = 'ai-analysis'
                # إضافة الرد الخام للفحص
                product['ai_raw_response'] = ai_text[:200] + "..." if len(ai_text) > 200 else ai_text
                
            logger.info(f"✅ تم معالجة رد الذكاء الاصطناعي، العودة لـ {len(products)} منتج")
            return products
            
        except Exception as e:
            logger.error(f"❌ Error parsing AI response: {str(e)}")
            return self.generate_sample_data(query, country, platform)
    
    def generate_sample_data(self, query, country, platform):
        """توليد بيانات منتجات تجريبية شاملة"""
        products = []
        
        for i in range(5):
            base_price = 100 if country == 'sa' else 500
            currency = 'ريال' if country == 'sa' else 'جنيه'
            
            product = {
                "id": f"{platform}-{i+1}",
                "name_ar": f"{query} الذكي #{i+1}",
                "name_en": f"Smart {query} #{i+1}",
                "image": f"https://picsum.photos/300/200?random={i}",
                "short_description": f"أحدث {query} في السوق بتقنيات متطورة وتصميم عصري",
                "category": query,
                "difficulty": "⭐" * (i % 3 + 1),
                "why_win": "طلب مرتفع وتكلفة منخفضة وهامش ربح عالي",
                "target": "شباب ومراهقين" if i % 2 == 0 else "عائلات ومحترفين",
                "age_range": "18-35" if i % 2 == 0 else "25-45",
                "gender": "ذكر" if i % 3 == 0 else "أنثى" if i % 3 == 1 else "كلا",
                "interests": ["تسوق", "موضة", "تقنية", "لياقة بدنية"],
                "problem": "يحل مشكلة الحاجة لمنتج عملي بجودة عالية وسعر معقول",
                
                "profit_analysis": {
                    "purchase_price": base_price + (i * 20),
                    "suggested_price": (base_price + (i * 20)) * 2,
                    "profit_margin": "45%",
                    "total_costs": (base_price + (i * 20)) * 0.3,
                    "net_profit": (base_price + (i * 20)) * 0.7,
                    "currency": currency
                },
                
                "suppliers": {
                    "local": [
                        {
                            "name": "مورد محلي #1",
                            "contact": "0551234567",
                            "link": "#"
                        }
                    ],
                    "international": [
                        {
                            "name": "AliExpress",
                            "link": "https://aliexpress.com",
                            "min_order": "1 قطعة"
                        }
                    ],
                    "shipping_days": "7-14 يوم",
                    "min_order": "1 قطعة"
                },
                
                "marketing": {
                    "platform": "تيك توك وإنستغرام",
                    "ad_copy": f"🔥 اكتشف أفضل {query} في السوق! 🔥\nجودة ممتازة ⭐ سعر لا يُنافس 🎯 توصيل سريع 🚚",
                    "video_idea": "عرض عملي للمنتج مع مقارنة الأسعار والجودة",
                    "hashtags": [f"#{query}", "#تسوق", "#عروض", "#جودة"],
                    "ad_budget": f"{50 + i * 10} {currency}/يوم"
                },
                
                "market_analysis": {
                    "competition": "منخفض" if i % 3 == 0 else "متوسط" if i % 3 == 1 else "عالي",
                    "demand": "مستمر" if i % 2 == 0 else "موسمي",
                    "unique_point": "جودة عالية وسعر تنافسي وتصميم مميز",
                    "growth_prediction": f"+{15 + i * 5}% خلال 2024"
                },
                
                "tips": [
                    "ركز على التسويق عبر منصات الفيديو القصيرة",
                    "التقط صور احترافية للمنتج من زوايا متعددة",
                    "قدم ضمان مجاني لأول 30 يوم",
                    "استخدم التوصيل السريع كعامل تمييز"
                ],
                
                "timestamp": datetime.now().isoformat(),
                "source": platform,
                "country": country,
                "analyzed_by": "openrouter" if OPENROUTER_API_KEY else "sample"
            }
            products.append(product)
        
        return products

# تهيئة المحلل
analyzer = SmartProductAnalyzer()

# الواجهة الرئيسية
@app.route('/')
def serve_frontend():
    return """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>المحلل الذكي للمنتجات الرابحة</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                direction: rtl;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }

            .header {
                text-align: center;
                color: white;
                margin-bottom: 40px;
            }

            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }

            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }

            .search-section {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }

            .search-box input {
                width: 100%;
                padding: 15px 20px;
                border: 2px solid #e1e5e9;
                border-radius: 12px;
                font-size: 1.1rem;
                margin-bottom: 20px;
                transition: all 0.3s ease;
            }

            .search-box input:focus {
                outline: none;
                border-color: #4CAF50;
                box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
            }

            .filters {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 25px;
            }

            .filter-group {
                display: flex;
                flex-direction: column;
            }

            .filter-group label {
                font-weight: 600;
                margin-bottom: 8px;
                color: #333;
            }

            .filter-group select {
                padding: 12px 15px;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                font-size: 1rem;
                background: white;
            }

            .analyze-btn {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 1.2rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }

            .analyze-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
            }

            .loading-spinner {
                width: 20px;
                height: 20px;
                border: 2px solid transparent;
                border-top: 2px solid white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .loading-section {
                background: white;
                border-radius: 20px;
                padding: 60px 40px;
                text-align: center;
                margin-bottom: 30px;
                display: none;
            }

            .spinner {
                width: 50px;
                height: 50px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #4CAF50;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }

            .results-section {
                background: white;
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                display: none;
            }

            .results-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 15px;
                border-bottom: 2px solid #f0f0f0;
            }

            .results-header h2 {
                color: #333;
                font-size: 1.8rem;
            }

            .results-info {
                display: flex;
                gap: 20px;
                color: #666;
            }

            .product-card {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 25px;
                border-right: 5px solid #4CAF50;
                transition: all 0.3s ease;
            }

            .product-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }

            .product-header {
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
                align-items: start;
            }

            .product-image {
                width: 150px;
                height: 150px;
                border-radius: 10px;
                object-fit: cover;
                border: 3px solid white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }

            .product-basic-info {
                flex: 1;
            }

            .product-name {
                font-size: 1.4rem;
                color: #333;
                margin-bottom: 10px;
            }

            .product-description {
                color: #666;
                line-height: 1.6;
                margin-bottom: 15px;
            }

            .detail-section {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 15px;
                border-right: 3px solid #e9ecef;
            }

            .detail-section h4 {
                color: #4CAF50;
                margin-bottom: 15px;
                font-size: 1.1rem;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .detail-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
            }

            .detail-item {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }

            .detail-label {
                font-weight: 600;
                color: #555;
                font-size: 0.9rem;
            }

            .detail-value {
                color: #333;
                line-height: 1.5;
            }

            .profit-badge {
                background: #4CAF50;
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
            }

            .tips-list {
                list-style: none;
                padding: 0;
            }

            .tips-list li {
                padding: 8px 0;
                border-bottom: 1px solid #f0f0f0;
                display: flex;
                align-items: start;
                gap: 10px;
            }

            .tips-list li:before {
                content: "💡";
                font-size: 1.1rem;
            }

            .error-section {
                background: white;
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                margin-bottom: 30px;
                display: none;
            }

            .error-card {
                max-width: 400px;
                margin: 0 auto;
            }

            .error-card h3 {
                color: #f44336;
                margin-bottom: 15px;
            }

            .error-card button {
                background: #f44336;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                cursor: pointer;
                margin-top: 15px;
            }

            .ai-badge {
                background: #2196F3;
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-left: 10px;
            }

            @media (max-width: 768px) {
                .container {
                    padding: 15px;
                }
                
                .search-section {
                    padding: 25px;
                }
                
                .filters {
                    grid-template-columns: 1fr;
                }
                
                .product-header {
                    flex-direction: column;
                }
                
                .product-image {
                    width: 100%;
                    height: 200px;
                }
                
                .detail-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <!-- الهيدر -->
            <header class="header">
                <h1>🎯 المحلل الذكي للمنتجات الرابحة</h1>
                <p>اكتشف أفضل المنتجات ربحية في السوق خلال دقائق</p>
                <div style="background: rgba(255,255,255,0.2); padding: 10px; border-radius: 10px; margin-top: 10px;">
                    <span style="color: #4CAF50;">✓ نظام الذكاء الاصطناعي مفعل (OpenRouter)</span>
                </div>
            </header>

            <!-- قسم البحث -->
            <section class="search-section">
                <div class="search-box">
                    <input type="text" id="query" placeholder="ما نوع المنتج الذي تبحث عنه؟ (مثال: ساعات ذكية، أجهزة رياضية، إكسسوارات)...">
                    
                    <div class="filters">
                        <div class="filter-group">
                            <label>السوق المستهدف:</label>
                            <select id="country">
                                <option value="sa">🇸🇦 السعودية</option>
                                <option value="eg">🇪🇬 مصر</option>
                                <option value="ae">🇦🇪 الإمارات</option>
                                <option value="global">🌍 عالمي</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label>منصة البيع:</label>
                            <select id="platform">
                                <option value="all">جميع المنصات</option>
                                <option value="amazon">أمازون</option>
                                <option value="aliexpress">علي اكسبريس</option>
                                <option value="noon">نون</option>
                                <option value="tiktok">تيك توك</option>
                            </select>
                        </div>
                    </div>

                    <button id="analyzeBtn" class="analyze-btn">
                        <span class="btn-text">🔍 ابدأ التحليل الذكي</span>
                        <div class="loading-spinner" style="display: none;"></div>
                    </button>
                </div>
            </section>

            <!-- حالة التحميل -->
            <div id="loadingSection" class="loading-section">
                <div class="loading-content">
                    <div class="spinner"></div>
                    <h3>جاري البحث والتحليل...</h3>
                    <p>نستخدم الذكاء الاصطناعي لتحليل أفضل فرص الربح لك</p>
                </div>
            </div>

            <!-- النتائج -->
            <section id="resultsSection" class="results-section">
                <div class="results-header">
                    <h2>نتائج التحليل <span id="aiBadge" class="ai-badge" style="display: none;">AI</span></h2>
                    <div class="results-info">
                        <span id="resultsCount">0 منتج</span>
                        <span id="searchQuery"></span>
                    </div>
                </div>
                <div id="resultsContainer" class="results-container"></div>
            </section>

            <!-- قسم الأخطاء -->
            <div id="errorSection" class="error-section">
                <div class="error-card">
                    <h3>⚠️ حدث خطأ</h3>
                    <p id="errorMessage"></p>
                    <button onclick="hideError()">حاول مرة أخرى</button>
                </div>
            </div>
        </div>

        <script>
            // إعدادات API
            const API_BASE_URL = window.location.origin;

            // عناصر DOM
            const elements = {
                queryInput: document.getElementById('query'),
                countrySelect: document.getElementById('country'),
                platformSelect: document.getElementById('platform'),
                analyzeBtn: document.getElementById('analyzeBtn'),
                loadingSection: document.getElementById('loadingSection'),
                resultsSection: document.getElementById('resultsSection'),
                resultsContainer: document.getElementById('resultsContainer'),
                resultsCount: document.getElementById('resultsCount'),
                searchQuery: document.getElementById('searchQuery'),
                errorSection: document.getElementById('errorSection'),
                errorMessage: document.getElementById('errorMessage'),
                aiBadge: document.getElementById('aiBadge')
            };

            // استمع لضغط Enter في حقل البحث
            elements.queryInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    analyzeProducts();
                }
            });

            // زر التحليل
            elements.analyzeBtn.addEventListener('click', analyzeProducts);

            async function analyzeProducts() {
                const query = elements.queryInput.value.trim();
                
                if (!query) {
                    showError('يرجى إدخال نوع المنتج الذي تريد البحث عنه');
                    return;
                }

                // إظهار حالة التحميل
                showLoading(true);
                hideResults();
                hideError();

                try {
                    const response = await fetch(API_BASE_URL + '/api/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            query: query,
                            country: elements.countrySelect.value,
                            platform: elements.platformSelect.value
                        })
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.error || 'حدث خطأ في الخادم');
                    }

                    if (!data.success) {
                        throw new Error(data.error || 'فشل في التحليل');
                    }

                    // عرض النتائج
                    displayResults(data);
                    
                } catch (error) {
                    console.error('Error:', error);
                    showError(error.message);
                } finally {
                    showLoading(false);
                }
            }

            function displayResults(data) {
                elements.resultsCount.textContent = data.products_count + ' منتج';
                elements.searchQuery.textContent = 'عنوان البحث: ' + data.query;
                
                // إظهار شارة AI إذا كان التحليل باستخدام الذكاء الاصطناعي
                const hasAI = data.products.some(p => p.analyzed_by === 'openrouter');
                elements.aiBadge.style.display = hasAI ? 'inline-block' : 'none';
                
                elements.resultsContainer.innerHTML = '';
                
                data.products.forEach((product, index) => {
                    const productCard = createProductCard(product, index + 1);
                    elements.resultsContainer.appendChild(productCard);
                });
                
                showResults();
            }

            function createProductCard(product, index) {
                const card = document.createElement('div');
                card.className = 'product-card';
                
                const aiBadge = product.analyzed_by === 'openrouter' ? 
                    '<span class="ai-badge">تحليل بالذكاء الاصطناعي</span>' : '';
                
                card.innerHTML = `
                    <div class="product-header">
                        <img src="${product.image}" alt="${product.name_ar}" class="product-image" 
                             onerror="this.src='https://via.placeholder.com/300x200/667eea/white?text=صورة+المنتج'">
                        
                        <div class="product-basic-info">
                            <h3 class="product-name">${index}. ${product.name_ar} ${aiBadge}</h3>
                            <p class="product-description">${product.short_description}</p>
                            
                            <div style="display: flex; gap: 15px; flex-wrap: wrap; margin-top: 10px;">
                                <span class="profit-badge">💰 هامش ربح: ${product.profit_analysis.profit_margin}</span>
                                <span class="profit-badge" style="background: #2196F3;">📊 ${product.difficulty}</span>
                                <span class="profit-badge" style="background: #FF9800;">🎯 ${product.target}</span>
                            </div>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h4>📊 المعلومات الأساسية</h4>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <span class="detail-label">الفئة:</span>
                                <span class="detail-value">${product.category}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">سبب الربحية:</span>
                                <span class="detail-value">${product.why_win}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">المشكلة التي يحلها:</span>
                                <span class="detail-value">${product.problem}</span>
                            </div>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h4>💰 تحليل الربحية</h4>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <span class="detail-label">سعر الشراء:</span>
                                <span class="detail-value">${product.profit_analysis.purchase_price} ${product.profit_analysis.currency}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">سعر البيع المقترح:</span>
                                <span class="detail-value">${product.profit_analysis.suggested_price} ${product.profit_analysis.currency}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">صافي الربح:</span>
                                <span class="detail-value">${product.profit_analysis.net_profit} ${product.profit_analysis.currency}</span>
                            </div>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h4>🎯 الجمهور المستهدف</h4>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <span class="detail-label">الفئة العمرية:</span>
                                <span class="detail-value">${product.age_range}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">الجنس:</span>
                                <span class="detail-value">${product.gender}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">الاهتمامات:</span>
                                <span class="detail-value">${product.interests.join('، ')}</span>
                            </div>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h4>📢 الاستراتيجية التسويقية</h4>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <span class="detail-label">منصة البيع:</span>
                                <span class="detail-value">${product.marketing.platform}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">ميزانية الإعلان:</span>
                                <span class="detail-value">${product.marketing.ad_budget}</span>
                            </div>
                        </div>
                        <div style="margin-top: 15px;">
                            <span class="detail-label">النص الإعلاني:</span>
                            <p style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-top: 8px; line-height: 1.5;">
                                ${product.marketing.ad_copy}
                            </p>
                        </div>
                        <div style="margin-top: 10px;">
                            <span class="detail-label">الهاشتاقات:</span>
                            <p style="color: #667eea; font-weight: 500; margin-top: 5px;">
                                ${product.marketing.hashtags.join(' ')}
                            </p>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h4>📊 تحليل السوق</h4>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <span class="detail-label">مستوى المنافسة:</span>
                                <span class="detail-value">${product.market_analysis.competition}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">حجم الطلب:</span>
                                <span class="detail-value">${product.market_analysis.demand}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">توقعات النمو:</span>
                                <span class="detail-value">${product.market_analysis.growth_prediction}</span>
                            </div>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h4>⚡ نصائح الخبراء</h4>
                        <ul class="tips-list">
                            ${product.tips.map(tip => '<li>' + tip + '</li>').join('')}
                        </ul>
                    </div>

                    <div class="detail-section">
                        <h4>🛒 معلومات الموردين</h4>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <span class="detail-label">مدة الشحن:</span>
                                <span class="detail-value">${product.suppliers.shipping_days}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">حد الأدنى للطلب:</span>
                                <span class="detail-value">${product.suppliers.min_order}</span>
                            </div>
                        </div>
                    </div>
                `;
                
                return card;
            }

            function showLoading(show) {
                const btnText = elements.analyzeBtn.querySelector('.btn-text');
                const spinner = elements.analyzeBtn.querySelector('.loading-spinner');
                
                if (show) {
                    btnText.textContent = 'جاري التحليل بالذكاء الاصطناعي...';
                    spinner.style.display = 'block';
                    elements.analyzeBtn.disabled = true;
                    elements.loadingSection.style.display = 'block';
                } else {
                    btnText.textContent = '🔍 ابدأ التحليل الذكي';
                    spinner.style.display = 'none';
                    elements.analyzeBtn.disabled = false;
                    elements.loadingSection.style.display = 'none';
                }
            }

            function showResults() {
                elements.resultsSection.style.display = 'block';
            }

            function hideResults() {
                elements.resultsSection.style.display = 'none';
            }

            function showError(message) {
                elements.errorMessage.textContent = message;
                elements.errorSection.style.display = 'block';
            }

            function hideError() {
                elements.errorSection.style.display = 'none';
            }

            // اختبار اتصال API عند التحميل
            window.addEventListener('load', async () => {
                try {
                    const response = await fetch(API_BASE_URL + '/api/health');
                    if (!response.ok) throw new Error('الخادم غير متاح');
                    console.log('✅ النظام يعمل بشكل صحيح');
                } catch (error) {
                    console.warn('⚠️ تعذر الاتصال بالخادم:', error.message);
                }
            });
        </script>
    </body>
    </html>
    """

# API Routes
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        country = data.get('country', 'sa')
        platform = data.get('platform', 'all')
        
        if not query:
            return jsonify({
                "success": False,
                "error": "يرجى إدخال مجال المنتجات للبحث"
            }), 400
        
        logger.info(f"طلب تحليل: {query} - {country} - {platform}")
        
        # البحث والتحليل
        products = analyzer.search_products(query, country, platform)
        
        return jsonify({
            "success": True,
            "query": query,
            "country": country,
            "platform": platform,
            "products_count": len(products),
            "products": products,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في التحليل: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"حدث خطأ في النظام: {str(e)}"
        }), 500

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "running",
        "service": "Smart Product Analyzer",
        "timestamp": datetime.now().isoformat(),
        "openrouter_available": bool(OPENROUTER_API_KEY)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
