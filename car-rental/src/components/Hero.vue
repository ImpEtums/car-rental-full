<template>
  <section class="hero">
    <div class="content">
      <div class="background-box">
        <h1 class="hero-title">欢迎来到 Yotrip</h1>
        <p class="hero-description">
          您的租车旅程从这里开始，探索更多的可能性和优惠。
        </p>
        <router-link to="/car-showcase" class="cta-button">查看服务</router-link>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: "Hero"
};
</script>

<style scoped>
.hero {
  background: url('@/assets/images/bg_3.png') no-repeat center top;
  background-size: cover;
  width: 100%;
  height: 600px;
  margin: 0;
  padding: 0;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #ffffff;
  text-align: center;
}

.content {
  max-width: 600px;
  padding: 20px;
  position: relative;
}

.background-box {
  background: rgba(0, 0, 0, 0.4);
  padding: 20px 30px;
  border-radius: 15px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.hero-title {
  font-size: 3rem;
  margin-bottom: 10px;
}

.hero-description {
  font-size: 1.4rem;
  margin-bottom: 20px;
}

.cta-button {
  display: inline-block;
  background-color: #ffbb00;
  color: black;
  padding: 10px 20px;
  text-decoration: none;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.cta-button:hover {
  background-color: #e69603;
}
</style>