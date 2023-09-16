// Because snake case is the worst
#![allow(nonstandard_style)]
use aws_config as config;
use aws_sdk_polly as polly;
use aws_sdk_s3 as s3;
use lambda_http::{run, service_fn, Body, Error, Request, Response};
use polly::primitives::ByteStream;
use urlencoding::decode;

async fn pollyHandler(pollyClient: &polly::Client, s3Client: &s3::Client, event: Request) -> Result<Response<Body>, Error> {
    let path = decode(event.uri().path())?;
    let split: Vec<&str> = path.split("/").collect();
    let translation = *split.last().unwrap();

    tracing::info!("pollyHandler invoked with {translation}");

    let resp;

    if translation.chars().count() < 15 {
        let result = pollyClient.synthesize_speech()
            .engine(polly::types::Engine::Standard)
            .language_code(polly::types::LanguageCode::KoKr)
            .output_format(polly::types::OutputFormat::Mp3)
            .text(translation.clone())
            .voice_id(polly::types::VoiceId::Seoyeon)
            .send()
            .await?;

        let bytes = result.audio_stream.collect().await?.to_vec();

        s3Client
            .put_object()
            .bucket("polly-bucket-us-west-2-434623153115")
            .key(format!("rust/{translation}"))
            .body(ByteStream::from(bytes.clone()))
            .send()
            .await?;

        resp = Response::builder()
            .status(200)
            .header("content-type", result.content_type.unwrap())
            .body(Body::Binary(bytes));
    } else {
        resp = Response::builder()
            .status(400)
            .body(Body::Empty);
    }
    Ok(resp.map_err(Box::new)?)
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        // disable printing the name of the module in every log line.
        .with_target(false)
        // disabling time is handy because CloudWatch will add the ingestion time.
        .without_time()
        .init();

    let config = config::load_from_env().await;
    let pollyClient = polly::Client::new(&config);
    let s3Client = s3::Client::new(&config);

    run(service_fn(|event: Request| {
        pollyHandler(&pollyClient, &s3Client, event)
    })).await
}
