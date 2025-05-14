<template>
    <div class="payment-page">
        <div class="payment-container">
            <h1 class="payment-title">请使用支付宝扫码支付</h1>
        
            <div class="qr-container">
                <img src="../assets/images/QRcode.jpg" alt="支付二维码" class="qr-code"/>
            </div>
        
            <div class="tip-text">
                <p>支付完成后，请点击下方按钮确认</p>
            </div>
        
            <button class="confirm-button" @click="handlePaymentConfirm">已完成支付</button>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const handlePaymentConfirm = () => {
    alert('支付确认成功！')
    router.push('/')
}
</script>

<style scoped>
.payment-page {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #f5f5f5;
    padding: 20px;
}

.payment-container {
    background: white;
    border-radius: 8px;
    padding: 40px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    max-width: 500px;
    width: 100%;
    text-align: center;
}

.payment-title {
    color: #333;
    font-size: 1.5em;
    margin-bottom: 30px;
}

.qr-container {
    margin: 30px auto;
    padding: 20px;
    background: #f8f8f8;
    border-radius: 8px;
    width: fit-content;
}

.qr-code {
    width: 200px;
    height: 200px;
    object-fit: contain;
}

.tip-text {
    color: #666;
    margin: 20px 0 30px;
}

.confirm-button {
    background-color: #fcd057;
    color: white;
    padding: 15px 40px;
    border: none;
    border-radius: 8px;
    font-size: 1.1em;
    cursor: pointer;
    transition: background-color 0.3s;
}

.confirm-button:hover {
    background-color: #ffa500;
}
</style>