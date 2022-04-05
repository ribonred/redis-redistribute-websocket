.PHONY: build
build-image:
	@docker build -t exchange-proxy:latest .
	@docker tag exchange-proxy:latest 736885973837.dkr.ecr.ap-east-1.amazonaws.com/exchange-proxy:python

push-image:
	@aws ecr get-login-password --region ap-east-1 | docker login --username AWS --password-stdin 736885973837.dkr.ecr.ap-east-1.amazonaws.com
	@docker push 736885973837.dkr.ecr.ap-east-1.amazonaws.com/exchange-proxy:python

