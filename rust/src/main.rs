mod secret;

use async_trait::async_trait;
use tokio;
use mattermost_api::prelude::*;

use secret::OAUTH;

use tungstenite;

struct Handler {}

#[async_trait]
impl WebsocketHandler for Handler {
    async fn callback(&self, message: WebsocketEvent) {
        println!("{:?}", message);
    }
}

#[tokio::main]
async fn main() {
    let auth = AuthenticationData::from_access_token(OAUTH);
    let mut api = Mattermost::new("https://mattermost.fysiksektionen.se", auth);
    api.store_session_token().await.unwrap();

    api.connect_to_websocket(Handler {}).await.unwrap();
}
