# Identidad de la cuenta usada solo para construir un nombre de bucket globalmente unico.
data "aws_caller_identity" "current" {}

locals {
  frontend_bucket_name = "${local.common_prefix}-frontend-${data.aws_caller_identity.current.account_id}"
  frontend_origin_id   = "${local.common_prefix}-frontend-s3-origin"
}

# Politica administrada de CloudFront recomendada para contenido estatico.
data "aws_cloudfront_cache_policy" "caching_optimized" {
  name = "Managed-CachingOptimized"
}

# Bucket privado que almacena los archivos compilados del frontend Vue.
resource "aws_s3_bucket" "frontend" {
  bucket = local.frontend_bucket_name

  tags = merge(
    local.common_tags,
    {
      Service = "Frontend"
    }
  )

  lifecycle {
    prevent_destroy = true
  }
}

# Deshabilita ACLs y fuerza propiedad del bucket para evitar permisos publicos accidentales.
resource "aws_s3_bucket_ownership_controls" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Bloqueo completo de acceso publico al bucket del frontend.
resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Cifrado del bucket con claves administradas por S3.
resource "aws_s3_bucket_server_side_encryption_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Versionado simple para conservar historico de objetos publicados sin cambiar el flujo de despliegue.
resource "aws_s3_bucket_versioning" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Origin Access Control para que CloudFront lea desde el bucket privado con SigV4.
resource "aws_cloudfront_origin_access_control" "frontend" {
  name                              = "${local.common_prefix}-frontend-oac"
  description                       = "OAC para servir el frontend ControlPyme desde S3 privado."
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# Distribucion CloudFront publica para servir la SPA Vue por HTTPS.
resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Frontend ControlPyme servido desde S3 privado."
  default_root_object = "index.html"
  price_class         = "PriceClass_100"

  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
    origin_id                = local.frontend_origin_id
  }

  default_cache_behavior {
    target_origin_id       = local.frontend_origin_id
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD", "OPTIONS"]
    cache_policy_id        = data.aws_cloudfront_cache_policy.caching_optimized.id
    compress               = true
  }

  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
    minimum_protocol_version       = "TLSv1.2_2021"
  }

  tags = merge(
    local.common_tags,
    {
      Service = "Frontend"
    }
  )
}

# Permite lectura de objetos solo desde la distribucion CloudFront del frontend.
data "aws_iam_policy_document" "frontend_bucket" {
  statement {
    sid    = "AllowCloudFrontReadOnly"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions = [
      "s3:GetObject",
    ]

    resources = [
      "${aws_s3_bucket.frontend.arn}/*",
    ]

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.frontend.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  policy = data.aws_iam_policy_document.frontend_bucket.json
}
