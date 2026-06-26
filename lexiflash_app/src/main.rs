mod components;
mod mock_data;
mod styles;

use dioxus::prelude::*;
use dioxus_desktop::{Config, LogicalSize, WindowBuilder};

fn main() {
    LaunchBuilder::desktop()
        .with_cfg(
            Config::new().with_window(
                WindowBuilder::new()
                    .with_title("LexiFlash")
                    .with_inner_size(LogicalSize::new(1160.0, 760.0))
                    .with_min_inner_size(LogicalSize::new(980.0, 660.0)),
            ),
        )
        .launch(App);
}

#[component]
fn App() -> Element {
    let decks = mock_data::mock_decks();
    let stats = mock_data::mock_stats();

    rsx! {
        style { "{styles::APP_CSS}" }
        div { class: "app",
            components::dashboard::Dashboard { decks, stats }
        }
    }
}
