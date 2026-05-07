# Database Update Required - Oxygen Level Field

## Important: Add Oxygen Level Column to Database

Your program has been updated to include **Oxygen Level (SpO2)** tracking. To ensure it works properly, you need to add the oxygen level column to your database.

### SQL Command to Run:

```sql
ALTER TABLE records ADD COLUMN oxygen_level FLOAT DEFAULT 98 AFTER dia_bp;
```

**Or if you're creating the table from scratch:**

```sql
CREATE TABLE records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    temp FLOAT,
    hr INT,
    sys_bp INT,
    dia_bp INT,
    oxygen_level FLOAT DEFAULT 98,
    current_medicine VARCHAR(100),
    disease VARCHAR(100),
    status VARCHAR(50),
    alt_medicine TEXT,
    date DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Steps:

1. Open your MySQL client (MySQL Workbench, phpMyAdmin, or terminal)
2. Select your `health_db` database
3. Run the ALTER TABLE command above
4. Verify the column was added:
   ```sql
   DESCRIBE records;
   ```

### Features Added:

✅ **Add Record Page:**
- New input field for Oxygen Level (SpO2) %
- Normal range: 95-100%
- Alert if below 95%

✅ **Dashboard:**
- Oxygen level column in health history table
- Green color if healthy (≥95%)
- Red color if low (<95%)

✅ **PDF Report:**
- Oxygen level included in downloaded report

✅ **Alert System:**
- "Low Oxygen" alert if SpO2 < 95%
- Contributes to disease prediction

### Normal Values:
| Category | SpO2 Range |
|----------|-----------|
| ✅ Normal | 95-100% |
| ⚠️ Low | 90-94% |
| 🚨 Critical | Below 90% |

Once you add the column to your database, everything will work perfectly!
