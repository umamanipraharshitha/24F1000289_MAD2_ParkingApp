<template>
  <div class="login-outer">
    <div class="login-container">
      <!-- Left: Parking Image -->
      <div class="login-image">
        <img :src="imageUrl" alt="Parking Lot" />
      </div>

      <!-- Right: Login Form -->
      <div class="login-form">
        <h2>Login</h2>

        <!-- Flash Messages -->
        <div v-if="messages.length">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="`alert alert-${message.category === 'error' ? 'danger' : message.category} alert-dismissible fade show`"
            role="alert"
          >
            {{ message.text }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
          </div>
        </div>

        <form method="POST">
          <div class="mb-3">
            <label for="role" class="form-label">Login as</label>
            <select class="form-select" id="role" name="role" required>
              <option value="user" selected>Student</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div class="mb-3">
            <label for="username" class="form-label">Username</label>
            <input type="text" class="form-control" id="username" name="username" placeholder="Enter username" required />
          </div>

          <div class="mb-3">
            <label for="email" class="form-label">Email address</label>
            <input type="email" class="form-control" id="email" name="email" placeholder="Enter email" required />
          </div>

          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input type="password" class="form-control" id="password" name="password" placeholder="Enter password" required />
          </div>

          <button type="submit" class="btn btn-primary">Login</button>
        </form>

        <div class="register-link">
          Don't have an account?
          <a :href="registerUrl">Register</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  props: {
    messages: {
      type: Array,
      default: () => [] // Expected format: [{ category: 'error', text: 'Invalid credentials' }]
    },
    imageUrl: {
      type: String,
      default: '/static/images/login.jpg' // This will work with Flask static folder
    },
    registerUrl: {
      type: String,
      default: '/register' // Flask route
    }
  }
};
</script>

<style scoped>
body {
  background: #ffffff;
  font-family: 'Poppins', Arial, sans-serif;
  min-height: 100vh;
}
.login-outer {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-container {
  max-width: 950px;
  width: 100%;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 0 32px rgba(0, 0, 0, 0.11);
  overflow: hidden;
  display: flex;
  min-height: 500px;
}
.login-image {
  flex: 1.1;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 0;
}
.login-image img {
  width: 95%;
  height: 95%;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 2px 18px rgba(0, 0, 0, 0.09);
}
.login-form {
  flex: 1;
  padding: 48px 36px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: #fff;
}
.login-form h2 {
  color: #23272b;
  margin-bottom: 32px;
  text-align: center;
  font-weight: 600;
  letter-spacing: 1px;
}
.form-label {
  color: #333;
  font-weight: 500;
}
.form-control,
.form-select {
  background: #ffffff;
  color: #23272b;
  border: 1px solid #9c9a9a;
  font-family: 'Poppins', Arial, sans-serif;
  border-radius: 6px;
  transition: border 0.2s;
}
.form-control:focus,
.form-select:focus {
  background: #18191a;
  color: #fff;
  border-color: #888;
  box-shadow: none;
}
.btn-primary {
  background: #23272b;
  border: none;
  width: 100%;
  margin-top: 12px;
  font-weight: 500;
  font-family: 'Poppins', Arial, sans-serif;
  border-radius: 6px;
  transition: background 0.2s;
}
.btn-primary:hover {
  background: #44474a;
}
.register-link {
  color: #848181;
  text-align: center;
  margin-top: 20px;
  font-size: 0.99rem;
}
.register-link a {
  color: #23272b;
  text-decoration: underline;
  font-weight: 500;
}
@media (max-width: 900px) {
  .login-container {
    flex-direction: column;
    min-width: unset;
    max-width: 98vw;
  }
  .login-image {
    height: 220px;
    padding: 16px 0;
  }
  .login-image img {
    min-height: 180px;
  }
}
@media (max-width: 600px) {
  .login-form {
    padding: 28px 12px;
  }
}
</style>
