use lp0003_sdk::run_two_distribution_demo;

fn main() {
    match run_two_distribution_demo() {
        Ok(report) => {
            println!("LP-0003 consumer demo: PASS");
            println!("distributions: {}", report.distribution_count);
            println!("unique claims: {}", report.unique_claim_count);
            println!(
                "duplicate rejections: {}",
                report.duplicate_rejections_observed
            );
            println!("status: {}", report.status);
        }
        Err(err) => {
            eprintln!("LP-0003 consumer demo: FAIL: {err}");
            std::process::exit(1);
        }
    }
}
