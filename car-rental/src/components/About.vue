<template>
  <div class="about-page">
    <img src="@/assets/images/about.png" alt="关于我们" />
  </div>
</template>

<script>
export default {
  name: "About"
};
</script>

<style scoped>
.about-page {
  width: 100vw;
  overflow-x: hidden; /* 防止水平滚动条 */
  position: relative;
}

.about-page img {
  width: 100%; /* 图片宽度填充屏幕 */
  height: auto; /* 保持高度自适应比例 */
  position: relative;
  top: -80px;
}
</style>
