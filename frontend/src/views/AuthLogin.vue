<template>
    <div class="screen-1">
        <img 
      class="logo" 
      src="@/assets/sdrIde.svg" 
      alt="Logo" 
      width="180" 
      height="180"
    >
      <div class="email">
        <label for="email">邮箱</label>
        <div class="sec-2">
          <ion-icon name="mail-outline"></ion-icon>
          <input type="email" name="email" placeholder="输入邮箱" v-model="email" />
        </div>
      </div>
      <div class="password">
        <label for="password">密码</label>
        <div class="sec-2">
          <ion-icon name="lock-closed-outline"></ion-icon>
          <input class="pas" :type="showPassword ? 'text' : 'password'" name="password" placeholder="输入密码" v-model="password" />
          <ion-icon class="show-hide" :name="showPassword ? 'eye-off-outline' : 'eye-outline'" @click="togglePassword"></ion-icon>
        </div>
      </div>
      <button class="login" @click="handleLogin">登录</button>
      <div class="footer">
        <span @click="handleRegister">注册</span>
        <span @click="handleForgotPassword">忘记密码?</span>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'Login',
    data() {
      return {
        email: '',
        password: '',
        showPassword: false
      }
    },
    methods: {
      togglePassword() {
        this.showPassword = !this.showPassword;
      },
      handleLogin() {
        // 登录逻辑
        console.log('登录', {
          email: this.email,
          password: this.password
        });
        // 可以在这里添加表单验证和API调用
      },
      handleRegister() {
        // 注册逻辑，通常是跳转到注册页面
        console.log('跳转到注册页面');
      },
      handleForgotPassword() {
        // 忘记密码逻辑，通常是跳转到密码重置页面
        console.log('跳转到忘记密码页面');
      }
    }
  }
  </script>
  
  <style >
  * {
    font-family: "Poppins";
  }
  body {
    user-select: none;
    overflow-y: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #dde5f4;  /**浅蓝色**/
    height: 120vh;
  }
  .screen-1 {
    background: #f1f7fe;
    padding: 2em;
    display: flex;
    flex-direction: column;
    border-radius: 30px;
    box-shadow: 0 0 2em #e6e9f9;
    gap: 2em;
  }
  .screen-1 .logo {
    margin-top: 2em;
    background-color: #f1f7fe;
  }
  .screen-1 .email {
    background: white;
    box-shadow: 0 0 2em #e6e9f9;
    padding: 1em;
    display: flex;
    flex-direction: column;
    gap: 0.5em;
    border-radius: 20px;
    color: #4d4d4d;
    margin-top: 4em;
  }
  .screen-1 .email input {
    outline: none;
    border: none;
  }
  .screen-1 .email input::placeholder {
    color: black;
    font-size: 0.9em;
  }
  .screen-1 .email ion-icon {
    color: #4d4d4d;
    margin-bottom: -0.2em;
  }
  .screen-1 .password {
    background: white;
    box-shadow: 0 0 2em #e6e9f9;
    padding: 1em;
    display: flex;
    flex-direction: column;
    gap: 0.5em;
    border-radius: 20px;
    color: #4d4d4d;
  }
  .screen-1 .password input {
    outline: none;
    border: none;
  }
  .screen-1 .password input::placeholder {
    color: black;
    font-size: 0.9em;
  }
  .screen-1 .password ion-icon {
    color: #4d4d4d;
    margin-bottom: -0.2em;
  }
  .screen-1 .password .show-hide {
    margin-right: -5em;
    cursor: pointer;
  }
  .screen-1 .login {
    padding: 1em;
    background: #3e4684;
    color: white;
    border: none;
    border-radius: 30px;
    font-weight: 600;
  }
  .screen-1 .footer {
    display: flex;
    justify-content: space-around;
    font-size: 0.7em;
    color: #5e5e5e;
    gap: 14em;
    padding-bottom: 10em;
  }
  .screen-1 .footer span {
    cursor: pointer;
  }
  button {
    cursor: pointer;
  }
  </style>
  