//! A deliberately small crate with no database, no CI and no infra.

pub fn add(a: i64, b: i64) -> i64 {
    a + b
}

pub fn describe(n: i64) -> String {
    if n > 0 { "positive".into() } else { "non-positive".into() }
}
