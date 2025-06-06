<template>
  <div class="order-list-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>我的订单</h1>
      <div class="order-stats">
        <div class="stat-item">
          <span class="stat-number">{{ totalOrders }}</span>
          <span class="stat-label">总订单</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ pendingOrders }}</span>
          <span class="stat-label">待处理</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ completedOrders }}</span>
          <span class="stat-label">已完成</span>
        </div>
      </div>
    </div>

    <!-- 订单筛选 -->
    <div class="order-filters">
      <div class="filter-tabs">
        <button 
          v-for="status in orderStatuses" 
          :key="status.value"
          :class="['filter-tab', { active: activeFilter === status.value }]"
          @click="setActiveFilter(status.value)"
        >
          {{ status.label }}
        </button>
      </div>
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索订单号或车辆信息"
          class="search-input"
        />
        <button class="search-btn" @click="searchOrders">🔍</button>
      </div>
    </div>

    <!-- 订单列表 -->
    <div class="orders-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载订单中...</p>
      </div>
      
      <div v-else-if="filteredOrders.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>暂无订单</h3>
        <p>您还没有任何订单记录</p>
        <router-link to="/car-showcase" class="create-order-btn">立即租车</router-link>
      </div>
      
      <div v-else class="order-grid">
        <div 
          v-for="order in paginatedOrders" 
          :key="order.order_id"
          class="order-card"
          :class="getOrderCardClass(order.status)"
        >
          <!-- 订单状态标签 -->
          <div class="order-status-badge" :class="getStatusClass(order.status)">
            {{ order.status_description }}
          </div>
          
          <!-- 订单主要信息 -->
          <div class="order-main-info">
            <div class="order-image">
              <img :src="order.image || '/src/assets/images/c1.png'" :alt="order.name" />
            </div>
            <div class="order-details">
              <h3 class="order-title">{{ order.name }}</h3>
              <div class="order-meta">
                <span class="order-id">订单号: {{ String(order.order_id).padStart(6, '0') }}</span>
                <span class="order-date">{{ formatDateTime(order.order_time) }}</span>
              </div>
              <div class="rental-info">
                <div class="info-item">
                  <span class="label">租期:</span>
                  <span class="value">{{ order.rental_days }}天</span>
                </div>
                <div class="info-item">
                  <span class="label">取车时间:</span>
                  <span class="value">{{ formatDateTime(order.start_time) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">还车时间:</span>
                  <span class="value">{{ formatDateTime(order.end_time) }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 价格信息 -->
          <div class="order-pricing">
            <div class="price-main">
              <span class="price-label">总金额</span>
              <span class="price-value">¥{{ order.total_amount }}</span>
            </div>
            <div class="price-details">
              <div v-if="order.discount_amount > 0" class="discount">
                <span>优惠: -¥{{ order.discount_amount }}</span>
              </div>
              <div class="deposit">
                <span>押金: ¥{{ order.deposit }}</span>
              </div>
            </div>
          </div>
          
          <!-- 订单操作 -->
          <div class="order-actions">
            <button class="action-btn view-btn" @click="viewOrderDetail(order)">
              查看详情
            </button>
            <button 
              v-if="canCancelOrder(order)"
              class="action-btn cancel-btn"
              @click="cancelOrder(order)"
            >
              取消订单
            </button>
            <button 
              v-if="canPayOrder(order)"
              class="action-btn pay-btn"
              @click="payOrder(order)"
            >
              立即支付
            </button>
            <button 
              v-if="canDeleteOrder(order)"
              class="action-btn delete-btn"
              @click="deleteOrder(order)"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination">
      <button 
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
        class="page-btn"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ currentPage }} 页，共 {{ totalPages }} 页
      </span>
      <button 
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
        class="page-btn"
      >
        下一页
      </button>
    </div>

    <!-- 订单详情弹窗 -->
    <div v-if="showOrderDetail" class="modal-overlay" @click="closeOrderDetail">
      <div class="modal-content order-detail-modal" @click.stop>
        <div class="modal-header">
          <h2>订单详情</h2>
          <button class="close-btn" @click="closeOrderDetail">×</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedOrder" class="order-detail-content">
            <!-- 订单基本信息 -->
            <div class="detail-section">
              <h3>订单信息</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>订单号:</label>
                  <span>{{ String(selectedOrder.order_id).padStart(6, '0') }}</span>
                </div>
                <div class="detail-item">
                  <label>订单状态:</label>
                  <span :class="getStatusClass(selectedOrder.status)">{{ selectedOrder.status_description }}</span>
                </div>
                <div class="detail-item">
                  <label>下单时间:</label>
                  <span>{{ formatDateTime(selectedOrder.order_time) }}</span>
                </div>
                <div class="detail-item">
                  <label>更新时间:</label>
                  <span>{{ formatDateTime(selectedOrder.update_time) }}</span>
                </div>
              </div>
            </div>
            
            <!-- 租车信息 -->
            <div class="detail-section">
              <h3>租车信息</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>车辆ID:</label>
                  <span>{{ selectedOrder.car_id }}</span>
                </div>
                <div class="detail-item">
                  <label>租期:</label>
                  <span>{{ selectedOrder.rental_days }}天</span>
                </div>
                <div class="detail-item">
                  <label>取车门店:</label>
                  <span>门店{{ selectedOrder.pickup_store_id }}</span>
                </div>
                <div class="detail-item">
                  <label>还车门店:</label>
                  <span>门店{{ selectedOrder.return_store_id }}</span>
                </div>
                <div class="detail-item">
                  <label>预计取车:</label>
                  <span>{{ formatDateTime(selectedOrder.start_time) }}</span>
                </div>
                <div class="detail-item">
                  <label>预计还车:</label>
                  <span>{{ formatDateTime(selectedOrder.end_time) }}</span>
                </div>
                <div v-if="selectedOrder.actual_start_time" class="detail-item">
                  <label>实际取车:</label>
                  <span>{{ formatDateTime(selectedOrder.actual_start_time) }}</span>
                </div>
                <div v-if="selectedOrder.actual_end_time" class="detail-item">
                  <label>实际还车:</label>
                  <span>{{ formatDateTime(selectedOrder.actual_end_time) }}</span>
                </div>
              </div>
            </div>
            
            <!-- 费用信息 -->
            <div class="detail-section">
              <h3>费用明细</h3>
              <div class="price-breakdown">
                <div class="price-item">
                  <span>订单总额:</span>
                  <span class="price">¥{{ selectedOrder.total_amount }}</span>
                </div>
                <div class="price-item">
                  <span>押金:</span>
                  <span class="price">¥{{ selectedOrder.deposit }}</span>
                </div>
                <div v-if="selectedOrder.discount_amount > 0" class="price-item discount">
                  <span>优惠金额:</span>
                  <span class="price">-¥{{ selectedOrder.discount_amount }}</span>
                </div>
                <div class="price-item total">
                  <span>实付金额:</span>
                  <span class="price">¥{{ (selectedOrder.total_amount - selectedOrder.discount_amount).toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn secondary" @click="closeOrderDetail">关闭</button>
          <button v-if="canCancelOrder(selectedOrder)" class="btn danger" @click="cancelOrder(selectedOrder)">
            取消订单
          </button>
          <button v-if="canPayOrder(selectedOrder)" class="btn primary" @click="payOrder(selectedOrder)">
            立即支付
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { flaskApiService } from '../axios.js';

export default {
  name: 'OrderListPage',
  watch: {
    '$route'(to, from) {
      // 当路由变化到订单页面时重新获取数据
      if (to.path === '/orders') {
        this.fetchOrders();
      }
    }
  },
  data() {
    return {
      orders: [],
      loading: false,
      searchQuery: '',
      activeFilter: 'all',
      currentPage: 1,
      pageSize: 6,
      showOrderDetail: false,
      selectedOrder: null,
      orderStatuses: [
        { value: 'all', label: '全部订单' },
        { value: 0, label: '待支付' },
        { value: 1, label: '已支付' },
        { value: 2, label: '已取车' },
        { value: 3, label: '已还车' },
        { value: 4, label: '已取消' }
      ]
    };
  },
  computed: {
    totalOrders() {
      return this.orders.length;
    },
    pendingOrders() {
      return this.orders.filter(order => order.status === 0 || order.status === 1).length;
    },
    completedOrders() {
      return this.orders.filter(order => order.status === 3).length;
    },
    filteredOrders() {
      let filtered = this.orders;
      
      // 状态筛选
      if (this.activeFilter !== 'all') {
        filtered = filtered.filter(order => order.status === this.activeFilter);
      }
      
      // 搜索筛选
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(order => 
          order.name.toLowerCase().includes(query) ||
          String(order.order_id).includes(query) ||
          order.status_description.toLowerCase().includes(query)
        );
      }
      
      return filtered;
    },
    totalPages() {
      return Math.ceil(this.filteredOrders.length / this.pageSize);
    },
    paginatedOrders() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredOrders.slice(start, end);
    }
  },
  async mounted() {
    await this.fetchOrders();
  },
  methods: {
    async fetchOrders() {
      this.loading = true;
      const token = localStorage.getItem('token');
      
      if (!token) {
        this.$router.push('/login');
        return;
      }
      
      try {
        const response = await flaskApiService.get('/user_orders', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.data.status === 'success') {
          this.orders = response.data.orders;
        } else {
          console.error('获取订单失败:', response.data.message);
        }
      } catch (error) {
        console.error('获取订单数据失败:', error);
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          this.$router.push('/login');
        }
      } finally {
        this.loading = false;
      }
    },
    setActiveFilter(status) {
      this.activeFilter = status;
      this.currentPage = 1;
    },
    searchOrders() {
      this.currentPage = 1;
    },
    changePage(page) {
      this.currentPage = page;
    },
    viewOrderDetail(order) {
      this.selectedOrder = order;
      this.showOrderDetail = true;
    },
    closeOrderDetail() {
      this.showOrderDetail = false;
      this.selectedOrder = null;
    },
    async cancelOrder(order) {
      if (!confirm('确定要取消这个订单吗？')) return;
      
      try {
        // 这里应该调用取消订单的API
        console.log('取消订单:', order.order_id);
        // 刷新订单列表
        await this.fetchOrders();
      } catch (error) {
        console.error('取消订单失败:', error);
        alert('取消订单失败，请稍后重试');
      }
    },
    async payOrder(order) {
      // 跳转到支付页面
      this.$router.push({
        name: 'payment',
        query: { orderId: order.order_id }
      });
    },
    async deleteOrder(order) {
      if (!confirm('确定要删除这个订单吗？删除后无法恢复。')) return;
      
      try {
        // 这里应该调用删除订单的API
        console.log('删除订单:', order.order_id);
        // 刷新订单列表
        await this.fetchOrders();
      } catch (error) {
        console.error('删除订单失败:', error);
        alert('删除订单失败，请稍后重试');
      }
    },
    canCancelOrder(order) {
      return order.status === 0 || order.status === 1; // 待支付或已支付
    },
    canPayOrder(order) {
      return order.status === 0; // 待支付
    },
    canDeleteOrder(order) {
      return order.status === 3 || order.status === 4; // 已完成或已取消
    },
    getStatusClass(status) {
      const statusClasses = {
        0: 'status-pending',
        1: 'status-paid',
        2: 'status-picked',
        3: 'status-completed',
        4: 'status-cancelled'
      };
      return statusClasses[status] || 'status-unknown';
    },
    getOrderCardClass(status) {
      return {
        'order-pending': status === 0,
        'order-active': status === 1 || status === 2,
        'order-completed': status === 3,
        'order-cancelled': status === 4
      };
    },
    formatDateTime(dateString) {
      if (!dateString) return '-';
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
};
</script>

<style scoped>
.order-list-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.page-header h1 {
  margin: 0 0 20px 0;
  font-size: 2.5rem;
  font-weight: 600;
}

.order-stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

/* 筛选区域 */
.order-filters {
  background: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.filter-tabs {
  display: flex;
  gap: 10px;
}

.filter-tab {
  padding: 8px 16px;
  border: 2px solid #e1e5e9;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.filter-tab:hover {
  border-color: #667eea;
  color: #667eea;
}

.filter-tab.active {
  background: #667eea;
  border-color: #667eea;
  color: white;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-input {
  padding: 10px 15px;
  border: 2px solid #e1e5e9;
  border-radius: 25px;
  width: 250px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
}

.search-btn {
  padding: 10px 15px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.3s ease;
}

.search-btn:hover {
  background: #5a6fd8;
}

/* 订单容器 */
.orders-container {
  min-height: 400px;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.create-order-btn {
  display: inline-block;
  padding: 12px 24px;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 25px;
  margin-top: 20px;
  transition: background 0.3s ease;
}

.create-order-btn:hover {
  background: #5a6fd8;
}

/* 订单网格 */
.order-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.order-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  position: relative;
  border-left: 4px solid #e1e5e9;
}

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.order-card.order-pending {
  border-left-color: #f39c12;
}

.order-card.order-active {
  border-left-color: #3498db;
}

.order-card.order-completed {
  border-left-color: #27ae60;
}

.order-card.order-cancelled {
  border-left-color: #e74c3c;
}

.order-status-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-paid {
  background: #d1ecf1;
  color: #0c5460;
}

.status-picked {
  background: #d4edda;
  color: #155724;
}

.status-completed {
  background: #d4edda;
  color: #155724;
}

.status-cancelled {
  background: #f8d7da;
  color: #721c24;
}

.order-main-info {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.order-image {
  flex-shrink: 0;
}

.order-image img {
  width: 80px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
}

.order-details {
  flex: 1;
}

.order-title {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.order-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
  font-size: 0.85rem;
  color: #666;
}

.rental-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  font-size: 0.85rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
}

.info-item .label {
  color: #666;
}

.info-item .value {
  font-weight: 500;
  color: #333;
}

.order-pricing {
  border-top: 1px solid #eee;
  padding-top: 15px;
  margin-bottom: 15px;
}

.price-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.price-label {
  font-weight: 600;
  color: #333;
}

.price-value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #e74c3c;
}

.price-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #666;
}

.discount {
  color: #27ae60;
}

.order-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.view-btn {
  background: #f8f9fa;
  color: #495057;
  border: 1px solid #dee2e6;
}

.view-btn:hover {
  background: #e9ecef;
}

.cancel-btn {
  background: #ffc107;
  color: #212529;
}

.cancel-btn:hover {
  background: #e0a800;
}

.pay-btn {
  background: #28a745;
  color: white;
}

.pay-btn:hover {
  background: #218838;
}

.delete-btn {
  background: #dc3545;
  color: white;
}

.delete-btn:hover {
  background: #c82333;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
  padding: 20px;
}

.page-btn {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.page-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-weight: 500;
  color: #666;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.detail-section {
  margin-bottom: 25px;
}

.detail-section h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 1.1rem;
  border-bottom: 2px solid #667eea;
  padding-bottom: 5px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.detail-item label {
  font-weight: 500;
  color: #666;
}

.detail-item span {
  color: #333;
}

.price-breakdown {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
}

.price-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.price-item.discount {
  color: #27ae60;
}

.price-item.total {
  border-top: 2px solid #dee2e6;
  margin-top: 10px;
  padding-top: 15px;
  font-weight: bold;
  font-size: 1.1rem;
}

.price-item .price {
  font-weight: 600;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn.primary {
  background: #667eea;
  color: white;
}

.btn.primary:hover {
  background: #5a6fd8;
}

.btn.secondary {
  background: #6c757d;
  color: white;
}

.btn.secondary:hover {
  background: #5a6268;
}

.btn.danger {
  background: #dc3545;
  color: white;
}

.btn.danger:hover {
  background: #c82333;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .order-list-page {
    padding: 10px;
  }
  
  .page-header {
    padding: 20px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .order-stats {
    gap: 20px;
  }
  
  .order-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-tabs {
    flex-wrap: wrap;
  }
  
  .search-input {
    width: 100%;
  }
  
  .order-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    margin: 10px;
  }
}
</style>