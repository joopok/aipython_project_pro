from flask import jsonify, flash, redirect, url_for
import logging

logger = logging.getLogger(__name__)

def handle_error(message, error_type='error', is_ajax=True, redirect_endpoint='main.index', status_code=400, log_error=None):
    """
    통합된 에러 처리 함수
    
    Args:
        message: 사용자에게 보여줄 에러 메시지
        error_type: 에러 타입 (error, warning, info)
        is_ajax: AJAX 요청 여부
        redirect_endpoint: 리다이렉트할 엔드포인트
        status_code: HTTP 상태 코드
        log_error: 로그에 기록할 실제 에러 (Exception)
    """
    if log_error:
        logger.error(f"{message}: {str(log_error)}", exc_info=True)
    
    if is_ajax:
        return jsonify({
            'success': False,
            'message': message
        }), status_code
    else:
        flash(message, error_type)
        return redirect(url_for(redirect_endpoint))

def handle_success(message, redirect_endpoint=None, is_ajax=True, extra_data=None):
    """
    통합된 성공 응답 처리 함수
    
    Args:
        message: 성공 메시지
        redirect_endpoint: 리다이렉트할 엔드포인트
        is_ajax: AJAX 요청 여부
        extra_data: 추가 데이터 (dict)
    """
    if is_ajax:
        response = {
            'success': True,
            'message': message
        }
        if redirect_endpoint:
            response['redirect'] = url_for(redirect_endpoint)
        if extra_data:
            response.update(extra_data)
        return jsonify(response)
    else:
        flash(message, 'success')
        return redirect(url_for(redirect_endpoint or 'main.index'))

def json_response(data, status=200):
    """간단한 JSON 응답 생성"""
    return jsonify(data), status