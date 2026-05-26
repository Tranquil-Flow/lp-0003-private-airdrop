use lp0003_sdk::{run_demo_distribution, run_two_distribution_demo};

#[test]
fn sdk_runs_one_distribution_with_ten_unique_claims_and_duplicate_rejection() {
    let report = run_demo_distribution("distribution-a", 10, 100).expect("demo distribution");

    assert_eq!(report.distribution_label, "distribution-a");
    assert_eq!(report.successful_claims, 10);
    assert_eq!(report.unique_nullifiers, 10);
    assert!(report.duplicate_rejection_observed);
    assert_eq!(report.rejected_claims, 1);
}

#[test]
fn sdk_runs_two_distributions_with_twenty_total_claims() {
    let report = run_two_distribution_demo().expect("two distribution demo");

    assert_eq!(report.distribution_count, 2);
    assert_eq!(report.unique_claim_count, 20);
    assert!(report.duplicate_rejections_observed >= 2);
    assert_eq!(report.status, "SAFE_LANE_ONLY_NOT_FINAL_LEZ_EVIDENCE");
}
