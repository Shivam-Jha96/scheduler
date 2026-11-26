# Application Load Balancer with TLS 1.3 Termination (FR-NET-01, FR-NET-04)

resource "aws_lb" "ingress" {
  name                       = "schedulerbot-alb"
  internal                   = false
  load_balancer_type         = "application"
  drop_invalid_header_fields = true
  security_groups            = [aws_security_group.alb.id]
  subnets                    = aws_subnet.public[*].id

  tags = {
    Name = "schedulerbot-alb"
  }
}

resource "aws_lb_target_group" "api_gateway" {
  name        = "schedulerbot-api-tg"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 15
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = {
    Name = "schedulerbot-api-tg"
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.ingress.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.acm_certificate_arn != "" ? var.acm_certificate_arn : null

  # Default action returns 404 Not Found for unmapped paths
  default_action {
    type = "fixed-response"

    fixed_response {
      content_type = "application/json"
      message_body = "{\"error\": \"Not Found\", \"message\": \"SchedulerBot Ingress Endpoint\"}"
      status_code  = "404"
    }
  }
}

# Listener Rule 1: Route WhatsApp Webhook Ingress
resource "aws_lb_listener_rule" "webhook_ingress" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api_gateway.arn
  }

  condition {
    path_pattern {
      values = ["/webhooks/whatsapp"]
    }
  }
}

# Listener Rule 2: Route Health Checks
resource "aws_lb_listener_rule" "health_check" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 20

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api_gateway.arn
  }

  condition {
    path_pattern {
      values = ["/health"]
    }
  }
}
