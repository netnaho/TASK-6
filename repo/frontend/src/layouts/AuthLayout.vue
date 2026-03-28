<template>
  <div class="auth-layout">
    <section class="auth-brand section-card">
      <div class="tiny">OFFLINE COMPLIANCE PLATFORM</div>
      <h1>NutriDeclare</h1>
      <p class="muted">
        Securely manage health profiles, phased nutrition declarations, reviewer workflows, and compliance delivery records from one premium internal workspace.
      </p>
      <div class="auth-stats">
        <div>
          <strong>72h</strong>
          <span>Default secure link expiry</span>
        </div>
        <div>
          <strong>3 roles</strong>
          <span>Participant, reviewer, administrator</span>
        </div>
      </div>
    </section>

    <section class="auth-form-wrap">
      <router-view />
    </section>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 24px;
  padding: 24px;
}

.auth-brand {
  padding: 40px;
  display: grid;
  align-content: space-between;
  background: linear-gradient(135deg, rgba(10, 24, 61, 0.92), rgba(30, 94, 255, 0.84)), url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400" fill="none"%3E%3Ccircle cx="300" cy="120" r="100" fill="rgba(255,255,255,0.08)"/%3E%3Ccircle cx="70" cy="310" r="80" fill="rgba(255,255,255,0.06)"/%3E%3C/svg%3E');
  color: white;
}

.auth-brand h1 {
  font-size: clamp(2.6rem, 4vw, 4.4rem);
  margin: 8px 0 16px;
}

.auth-form-wrap {
  display: grid;
  align-items: center;
}

.auth-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.auth-stats div {
  background: rgba(255, 255, 255, 0.09);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 18px;
  padding: 16px;
  display: grid;
  gap: 4px;
}

.auth-stats strong {
  font-size: 1.3rem;
}

@media (max-width: 960px) {
  .auth-layout {
    grid-template-columns: 1fr;
  }

  .auth-brand {
    min-height: 280px;
  }
}
</style>
