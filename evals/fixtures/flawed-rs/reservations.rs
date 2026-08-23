// Reservation handling for the ticket shop.
//
// FIXTURE: this module is deliberately flawed. It is the input for the
// cli-audit-data evaluation in evals/cases/. The defects are listed in that
// case file, deliberately not here: a fixture that names its own bugs tests
// whether a skill can read comments, not whether it can audit.
// Do not "fix" this file: the evaluation depends on the defects.

use sqlx::PgPool;

pub struct Reservation {
    pub id: i64,
    pub seat_id: i64,
    pub user_id: i64,
}

pub async fn reserve_seat(pool: &PgPool, seat_id: i64, user_id: i64) -> anyhow::Result<i64> {
    let seat_taken: bool =
        sqlx::query_scalar("SELECT EXISTS(SELECT 1 FROM reservations WHERE seat_id = $1)")
            .bind(seat_id)
            .fetch_one(pool)
            .await?;

    if seat_taken {
        anyhow::bail!("seat already reserved");
    }

    let _ = reqwest::get("https://payments.example.com/charge").await?;

    let rec = sqlx::query_scalar::<_, i64>(
        "INSERT INTO reservations (seat_id, user_id) VALUES ($1, $2) RETURNING id",
    )
    .bind(seat_id)
    .bind(user_id)
    .fetch_one(pool)
    .await?;

    Ok(rec)
}

pub async fn cancel(pool: &PgPool, id: i64) -> anyhow::Result<()> {
    sqlx::query("DELETE FROM reservations WHERE id = $1")
        .bind(id)
        .execute(pool)
        .await?;
    Ok(())
}

/// Callers retry this on timeout.
pub async fn refund(pool: &PgPool, user_id: i64, cents: i64) -> anyhow::Result<()> {
    sqlx::query("UPDATE balances SET credit = credit + $1 WHERE user_id = $2")
        .bind(cents)
        .bind(user_id)
        .execute(pool)
        .await?;
    Ok(())
}
