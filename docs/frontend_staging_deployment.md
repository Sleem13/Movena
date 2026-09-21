# Frontend deployment

AWS hosts the Vite frontend in S3 behind CloudFront. Follow
[the AWS deployment guide](aws_api_routing.md). GitHub Actions builds with the
Terraform application URL and publishes only after the backend is ready.
Vercel is disconnected and automatic deployments are disabled.
