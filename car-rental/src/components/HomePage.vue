<template>
  <div class="home-page">
    <Hero />
    <CarRentalSelector />
    <!-- 新增 Highcharts 图表容器 -->
    <section class="chart-container">
      <h2 class="section-title">各城市网点数量</h2>
      <div id="city-branch-chart"></div>
    </section>
    <section class="car-showcase">
      <h2 class="section-title">精选车辆</h2>
      <div class="car-images">
        <div v-for="car in featuredCars" :key="car.id" class="car-item">
          <img :src="car.image" :alt="car.name" class="car-image" />
          <div class="car-info">
            <h2>{{ car.name }}</h2>
            <div class="car-features">
              <span>
                <img src="@/assets/images/icons/number-of-seats.png" alt="座位数" class="feature-icon" />
                {{ car.seats }}座
              </span>
              <span>
                <img src="@/assets/images/icons/energy-type.png" alt="燃料类型" class="feature-icon" />
                {{ car.fuelType }}
              </span>
              <span>
                <img src="@/assets/images/icons/gearbox-type.png" alt="变速箱类型" class="feature-icon" />
                {{ car.transmission }}
              </span>
            </div>
            <div class="price-action-row">
              <div class="car-price">
                <span class="price-symbol">¥</span>
                <span class="price-amount">{{ car.price }}</span>
                <span class="price-period">/天</span>
              </div>
              <router-link :to="{ name: 'showcase', params: { car: JSON.stringify(car) } }" class="book-button">立即预订</router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 原有的昨日车辆租赁成交次数图表 -->
    <section class="chart-container">
      <h2 class="section-title">昨日车辆租赁成交次数</h2>
      <div id="vehicle-rental-chart"></div>
    </section>

    <section class="qna-container">
      <h1 class="qna-title">常见问题</h1>
      <p class="qna-subtitle">每一个阶段，都值得留下美好时刻</p>
      <div class="qna-grid">
        <!-- Card 1 -->
        <div class="qna-card">
          <h3>Q1 租车需要哪些证件？</h3>
          <p>
            身份证：大陆用户驾驶员二代身份证，年满18周岁，有效期需超过当次租期一个月以上。
            <br>
            驾驶证：本人国内有效驾驶证（正副本），有效期需超过当次租期一个月以上。
            <br>
            外籍客户提供护照，有效期超过当次租期两个月以上。
          </p>
        </div>
        <!-- Card 2 -->
        <div class="qna-card">
          <h3>Q2 有哪些网络预订方式？</h3>
          <p>
            App：通过应用市场下载相关租车App进行预订。
            <br>
            小程序：在微信和支付宝平台搜索相关租车小程序进行预订。
            <br>
            触屏版：浏览器中输入指定网址进行预订。
          </p>
        </div>
        <!-- Card 3 -->
        <div class="qna-card">
          <h3>Q3 有哪些预订流程？</h3>
          <p>
            第一步：确定需要取还车的地址和时间。
            <br>
            第二步：选择取还车的网点和车型。
            <br>
            第三步：选择承租人。
            <br>
            第四步：订单确认，完成预订。
          </p>
        </div>
        <!-- Card 4 -->
        <div class="qna-card">
          <h3>Q4 可以开哪些发票？</h3>
          <p>
            国内租订单还车结算后以订单单位，为您开具增值税发票；支持电子发票和纸质发票。
          </p>
        </div>
        <!-- Card 5 -->
        <div class="qna-card">
          <h3>Q5 租车费用有哪些？</h3>
          <p>
            必缴费用包括：车辆租赁及服务费、基础服务费、车辆整备费。
            <br>
            其他费用包括：送车上门服务费，异地还车服务费等。
          </p>
        </div>
        <!-- Card 6 -->
        <div class="qna-card">
          <h3>Q6 可以选择哪些出行保障？</h3>
          <p>
            您可以购买尊享服务，享受全程无忧保障，提升出行体验。
          </p>
        </div>
      </div>
    </section>

    <section class="company-news">
      <div class="news-header">
        <h2 class="news-title">公司动态</h2>
        <a href="/news" class="more-news">更多新闻 >></a>
      </div>
      <div class="news-content">
        <div class="news-image">
          <img src="@/assets/images/company.jpg" alt="公司动态图片" />
        </div>
        <div class="news-list">
          <ul>
            <li>
              <a href="/news/1">我们凭借诚信经营的服务理念荣获2023中国汽车流通行业优秀会员</a>
              <span class="news-date">2023-11-17 14:54</span>
            </li>
            <li>
              <a href="/news/2">以“新”赋能行业发展，二手车亮相2023x国汽车流通行业年会</a>
              <span class="news-date">2023-11-16 14:57</span>
            </li>
            <li>
              <a href="/news/3">我们与杭师大汽车签署战略合作 向上融合共建未来自驾出行新生态</a>
              <span class="news-date">2023-11-16 14:52</span>
            </li>
            <li>
              <a href="/news/4">我们与闪动校园携手 开启出行市场跨业生态融合新篇章</a>
              <span class="news-date">2023-11-10 14:51</span>
            </li>
            <li>
              <a href="/news/5">9块9自驾去仓前/下沙！我们上线超值套餐回馈广大用户</a>
              <span class="news-date">2023-10-26 14:42</span>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <footer class="site-footer">
      <div class="footer-top">
        <div class="footer-column">
          <h4>Yotrip租车</h4>
          <ul>
            <li><a href="/about">关于我们</a></li>
            <li><a href="/contact">联系我们</a></li>
            <li><a href="/join">加入我们</a></li>
            <li><a href="/news">新闻中心</a></li>
            <li><a href="/qualifications">资质信息</a></li>
          </ul>
        </div>
        <div class="footer-column">
          <h4>合作伙伴</h4>
          <ul>
            <li><a href="/partners">投资者关系</a></li>
          </ul>
        </div>
        <div class="footer-column">
          <h4>其他服务</h4>
          <ul>
            <li><a href="/sitemap">网站导航</a></li>
            <li><a href="/privacy">隐私保护</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>友情链接：
          <a href="https://example1.com" target="_blank">旅游指南</a> |
          <a href="https://example2.com" target="_blank">自驾游推荐</a> |
          <a href="https://example3.com" target="_blank">城市租车服务</a>
        </p>
        <p>Copyright © 2024 Yotrip.com All Rights Reserved. 杭州 Yotrip 汽车租赁有限公司 杭ICP备12345678号</p>
      </div>
    </footer>

  </div>
</template>

<script>
import Hero from '../components/Hero.vue';
import CarRentalSelector from '../components/CarRentalSelector.vue';
import { useRouter } from 'vue-router';
import Highcharts from 'highcharts';
import { flaskApiService } from '../axios.js'; // 导入Flask API服务

import car1 from '../assets/images/car1.png';
import car2 from '../assets/images/car2.png';
import car3 from '../assets/images/car3.png';

export default {
  name: 'HomePage',
  components: {
    Hero,
    CarRentalSelector,
  },
  setup() {
    const router = useRouter();

    const handleCarBooking = (car) => {
      router.push({
        name: 'car-showcase',
        query: {
          carId: car.id,
          carName: car.name,
          price: car.price
        }
      });
    };

    // 从Redis获取城市网点数据并初始化图表
    const initCityBranchChart = async () => {
      try {
        const response = await flaskApiService.get('/api/redis/city-branches');
        const data = response.data;
        
        if (data.status === 'success') {
          const cityNames = Object.keys(data.data);
          const branchCounts = Object.values(data.data);

          Highcharts.chart('city-branch-chart', {
            chart: {
              type: 'column'
            },
            title: {
              text: null
            },
            xAxis: {
              categories: cityNames,
              crosshair: true
            },
            yAxis: {
              min: 0,
              title: {
                text: '网点个数'
              }
            },
            tooltip: {
              headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
              pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y} 个</b></td></tr>',
              footerFormat: '</table>',
              shared: true,
              useHTML: true
            },
            plotOptions: {
              column: {
                pointPadding: 0.2,
                borderWidth: 0
              }
            },
            series: [{
              name: '网点个数',
              data: branchCounts
            }]
          });
        }
      } catch (error) {
        console.error('获取城市网点数据失败:', error);
        // 如果Redis数据获取失败，使用默认数据
        const cityNames = ['上海', '浙江', '北京', '广州', '深圳'];
        const branchCounts = [10, 15, 8, 12, 9];
        
        Highcharts.chart('city-branch-chart', {
          chart: { type: 'column' },
          title: { text: null },
          xAxis: { categories: cityNames, crosshair: true },
          yAxis: { min: 0, title: { text: '网点个数' } },
          tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
              '<td style="padding:0"><b>{point.y} 个</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
          },
          plotOptions: { column: { pointPadding: 0.2, borderWidth: 0 } },
          series: [{ name: '网点个数', data: branchCounts }]
        });
      }
    };

    // 从Redis获取车辆租赁数据并初始化图表
    const initVehicleRentalChart = async () => {
      try {
        const response = await flaskApiService.get('/api/redis/vehicle-rentals');
        const data = response.data;
        
        if (data.status === 'success') {
          const vehicleNames = Object.keys(data.data);
          const rentalCounts = Object.values(data.data);

          Highcharts.chart('vehicle-rental-chart', {
            chart: {
              type: 'column'
            },
            title: {
              text: null
            },
            xAxis: {
              categories: vehicleNames,
              crosshair: true
            },
            yAxis: {
              min: 0,
              title: {
                text: '成交次数'
              }
            },
            tooltip: {
              headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
              pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y} 次</b></td></tr>',
              footerFormat: '</table>',
              shared: true,
              useHTML: true
            },
            plotOptions: {
              column: {
                pointPadding: 0.2,
                borderWidth: 0
              }
            },
            series: [{
              name: '成交次数',
              data: rentalCounts
            }]
          });
        }
      } catch (error) {
        console.error('获取车辆租赁数据失败:', error);
        // 如果Redis数据获取失败，使用默认数据
        const vehicleNames = ['本田雅阁', '本田思域', '丰田凯美瑞', '大众帕萨特', '现代索纳塔'];
        const rentalCounts = [20, 18, 22, 8, 6];
        
        Highcharts.chart('vehicle-rental-chart', {
          chart: { type: 'column' },
          title: { text: null },
          xAxis: { categories: vehicleNames, crosshair: true },
          yAxis: { min: 0, title: { text: '成交次数' } },
          tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
              '<td style="padding:0"><b>{point.y} 次</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
          },
          plotOptions: { column: { pointPadding: 0.2, borderWidth: 0 } },
          series: [{ name: '成交次数', data: rentalCounts }]
        });
      }
    };

    // 在组件挂载后初始化图表
    const onMounted = () => {
      initCityBranchChart();
      initVehicleRentalChart();
    };

    return {
      handleCarBooking,
      onMounted
    };
  },
  data() {
    return {
      featuredCars: [
        {
          id: 1,
          name: '本田雅阁',
          price: 358,
          seats: 5,
          fuelType: '汽油',
          transmission: '自动',
          image: car1
        },
        {
          id: 2,
          name: '本田思域',
          price: 328,
          seats: 5,
          fuelType: '汽油',
          transmission: '自动',
          image: car2
        },
        {
          id: 3,
          name: '丰田凯美瑞',
          price: 368,
          seats: 5,
          fuelType: '汽油',
          transmission: '自动',
          image: car3
        }
      ]
    };
  },
  mounted() {
    this.onMounted();
  }
};
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.car-showcase {
  width: 100%;
  padding: 50px 20px;
  text-align: center;
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 32px;
  font-weight: bold;
  font-family: 'Microsoft YaHei', sans-serif;
}

.car-images {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.car-item {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.car-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.car-info {
  padding: 16px;
}

.car-info h2 {
  font-size: 1.4rem;
  margin: 0 0 12px 0;
  color: #333;
}

.car-features {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.car-features span {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 0.9rem;
}

.feature-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
}

.price-action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.car-price {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.price-symbol {
  font-size: 1rem;
  color: #ff6b00;
}

.price-amount {
  font-size: 1.8rem;
  font-weight: bold;
  color: #ff6b00;
}

.price-period {
  color: #666;
  font-size: 0.9rem;
}

.book-button {
  padding: 8px 24px;
  background-color: #ffbb00;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
  width: auto;
  text-decoration: none;
}

.book-button:hover {
  background-color: #e69603;
}

.qna-container {
  width: 100%;
  max-width: 1200px;
  margin: 40px auto;
  text-align: center;
}

.qna-title {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 20px;
  font-weight: bold;
  font-family: 'Microsoft YaHei', sans-serif;
}

.qna-subtitle {
  font-size: 1.2rem;
  color: #777;
  margin-bottom: 40px;
}

.qna-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.qna-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  text-align: left;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.qna-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.qna-card h3 {
  font-size: 1rem;
  color: #ffbb00;
  margin-bottom: 10px;
  font-family: 'Microsoft YaHei', sans-serif;
}

.qna-card p {
  font-size: 0.9rem;
  color: #555;
  line-height: 1.5;
}

.company-news {
  width: 100%;
  max-width: 1200px;
  margin: 40px auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.news-title {
  font-size: 2rem;
  color: #333;
  font-weight: bold;
  font-family: 'Microsoft YaHei', sans-serif;
}

.more-news {
  font-size: 0.9rem;
  color: #ffbb00;
  text-decoration: none;
}

.more-news:hover {
  text-decoration: underline;
}

.news-content {
  display: flex;
  gap: 30px;
  align-items: flex-start;
}

.news-image img {
  width: 400px;
  height: auto;
  border-radius: 8px;
  object-fit: cover;
}

.news-list {
  flex: 1;
  text-align: left;
}

.news-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.news-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}

.news-list li a {
  text-decoration: none;
  color: #333;
  flex: 1;
}

.news-list li a:hover {
  color: #ffbb00;
}

.news-date {
  font-size: 0.9rem;
  color: #777;
  margin-left: 10px;
  white-space: nowrap;
}

.site-footer {
  background-color: #2b2b2b;
  color: #ddd;
  padding: 40px 20px;
  width: 100%;
}

.footer-top {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.footer-column {
  flex: 1;
}

.footer-column h4 {
  font-size: 1.2rem;
  color: #fff;
  margin-bottom: 15px;
  font-family: 'Microsoft YaHei', sans-serif;
}

.footer-column ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-column ul li {
  margin-bottom: 10px;
}

.footer-column ul li a {
  color: #ddd;
  text-decoration: none;
  font-size: 0.9rem;
}

.footer-column ul li a:hover {
  color: #ffbb00;
}

.footer-bottom {
  text-align: center;
  margin-top: 30px;
  border-top: 1px solid #444;
  padding-top: 20px;
  font-size: 0.8rem;
  color: #aaa;
}

.footer-bottom a {
  color: #ddd;
  text-decoration: none;
}

.footer-bottom a:hover {
  color: #ffbb00;
}

/* 新增图表容器样式 */
.chart-container {
  width: 100%;
  max-width: 1200px;
  margin: 40px auto;
  text-align: center;
}
</style>