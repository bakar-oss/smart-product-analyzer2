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
    errorMessage: document.getElementById('errorMessage')
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
        const response = await fetch(`${API_BASE_URL}/api/analyze`, {
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
    elements.resultsCount.textContent = `${data.products_count} منتج`;
    elements.searchQuery.textContent = `عنوان البحث: ${data.query}`;
    
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
    
    card.innerHTML = `
        <div class="product-header">
            ${product.image ? `
                <img src="${product.image}" alt="${product.name_ar}" class="product-image" 
                     onerror="this.src='https://via.placeholder.com/300x200/667eea/white?text=صورة+المنتج'">
            ` : ''}
            
            <div class="product-basic-info">
                <h3 class="product-name">${index}. ${product.name_ar} / ${product.name_en}</h3>
                <p class="product-description">${product.short_description}</p>
                
                <div style="display: flex; gap: 15px; flex-wrap: wrap; margin-top: 10px;">
                    <span class="profit-badge">💰 هامش ربح: ${product.profit_analysis?.profit_margin || 'N/A'}</span>
                    <span class="profit-badge" style="background: #2196F3;">📊 ${product.difficulty}</span>
                    <span class="profit-badge" style="background: #FF9800;">🎯 ${product.target}</span>
                </div>
            </div>
        </div>

        <!-- المعلومات الأساسية -->
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

        <!-- تحليل الربحية -->
        <div class="detail-section">
            <h4>💰 تحليل الربحية</h4>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">سعر الشراء:</span>
                    <span class="detail-value">${product.profit_analysis?.purchase_price} ${product.profit_analysis?.currency}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">سعر البيع المقترح:</span>
                    <span class="detail-value">${product.profit_analysis?.suggested_price} ${product.profit_analysis?.currency}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">صافي الربح:</span>
                    <span class="detail-value">${product.profit_analysis?.net_profit} ${product.profit_analysis?.currency}</span>
                </div>
            </div>
        </div>

        <!-- الجمهور المستهدف -->
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
                    <span class="detail-value">${product.interests?.join('، ') || ''}</span>
                </div>
            </div>
        </div>

        <!-- الاستراتيجية التسويقية -->
        <div class="detail-section">
            <h4>📢 الاستراتيجية التسويقية</h4>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">منصة البيع:</span>
                    <span class="detail-value">${product.marketing?.platform}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">ميزانية الإعلان:</span>
                    <span class="detail-value">${product.marketing?.ad_budget}</span>
                </div>
            </div>
            <div style="margin-top: 15px;">
                <span class="detail-label">النص الإعلاني:</span>
                <p style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-top: 8px; line-height: 1.5;">
                    ${product.marketing?.ad_copy}
                </p>
            </div>
            <div style="margin-top: 10px;">
                <span class="detail-label">الهاشتاقات:</span>
                <p style="color: #667eea; font-weight: 500; margin-top: 5px;">
                    ${product.marketing?.hashtags?.join(' ') || ''}
                </p>
            </div>
        </div>

        <!-- تحليل السوق -->
        <div class="detail-section">
            <h4>📊 تحليل السوق</h4>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">مستوى المنافسة:</span>
                    <span class="detail-value">${product.market_analysis?.competition}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">حجم الطلب:</span>
                    <span class="detail-value">${product.market_analysis?.demand}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">توقعات النمو:</span>
                    <span class="detail-value">${product.market_analysis?.growth_prediction}</span>
                </div>
            </div>
        </div>

        <!-- نصائح الخبراء -->
        <div class="detail-section">
            <h4>⚡ نصائح الخبراء</h4>
            <ul class="tips-list">
                ${product.tips?.map(tip => `<li>${tip}</li>`).join('') || '<li>لا توجد نصائح متاحة</li>'}
            </ul>
        </div>

        <!-- الموردين -->
        <div class="detail-section">
            <h4>🛒 معلومات الموردين</h4>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">مدة الشحن:</span>
                    <span class="detail-value">${product.suppliers?.shipping_days}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">حد الأدنى للطلب:</span>
                    <span class="detail-value">${product.suppliers?.min_order}</span>
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
        btnText.textContent = 'جاري التحليل...';
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
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (!response.ok) throw new Error('الخادم غير متاح');
        console.log('✅ النظام يعمل بشكل صحيح');
    } catch (error) {
        console.warn('⚠️ تعذر الاتصال بالخادم:', error.message);
    }
});
