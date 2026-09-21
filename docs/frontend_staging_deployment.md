# Frontend deployment

AWS hosts the Vite frontend in S3 behind CloudFront. Follow
[the AWS deployment guide](aws_api_routing.md). GitHub Actions builds with the
Terraform application URL and publishes only after the backend is ready.
The former Vercel project and configuration have been removed.
