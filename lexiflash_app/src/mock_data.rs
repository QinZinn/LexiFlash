#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Deck {
    pub title: String,
    pub vocab_count: u32,
    pub created_at: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StudyStats {
    pub learned_total: u32,
    pub streak_days: u32,
    pub due_today: u32,
}

pub fn mock_decks() -> Vec<Deck> {
    vec![
        Deck {
            title: "VnExpress — Kinh tế".to_string(),
            vocab_count: 128,
            created_at: "2026-06-20".to_string(),
        },
        Deck {
            title: "BBC — Technology".to_string(),
            vocab_count: 94,
            created_at: "2026-06-21".to_string(),
        },
        Deck {
            title: "Longform — Essays".to_string(),
            vocab_count: 56,
            created_at: "2026-06-24".to_string(),
        },
    ]
}

pub fn mock_stats() -> StudyStats {
    StudyStats {
        learned_total: 1_042,
        streak_days: 12,
        due_today: 38,
    }
}

