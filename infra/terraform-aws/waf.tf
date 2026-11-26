# AWS WAFv2 Ingress Protection with Rate Limiting (FR-NET-01)

resource "aws_wafv2_web_acl" "ingress_waf" {
  name        = "schedulerbot-ingress-waf"
  description = "Regional WAF protecting WhatsApp Webhook Ingress and ALB"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  # Rule 1: Rate-based rule limiting excessive single-IP webhook requests
  rule {
    name     = "RateLimitWhatsAppWebhooks"
    priority = 1

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"

        scope_down_statement {
          byte_match_statement {
            search_string         = "/webhooks/whatsapp"
            positional_constraint = "EXACTLY"

            field_to_match {
              uri_path {}
            }

            text_transformation {
              priority = 0
              type     = "NONE"
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitWhatsAppWebhooks"
      sampled_requests_enabled   = true
    }
  }

  # Rule 2: AWS Managed Rules Common Rule Set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }

  # Rule 3: AWS Managed Rules Known Bad Inputs Rule Set
  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesKnownBadInputsRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "SchedulerBotWafMetric"
    sampled_requests_enabled   = true
  }

  tags = {
    Name = "schedulerbot-ingress-waf"
  }
}

# Associate WAF WebACL with Application Load Balancer
resource "aws_wafv2_web_acl_association" "alb_assoc" {
  resource_arn = aws_lb.ingress.arn
  web_acl_arn  = aws_wafv2_web_acl.ingress_waf.arn
}
