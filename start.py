from app import create_app# WSGI 진입점 생성
application = create_app()

# 이는 개발 목적으로 사용되며, 실제 배포를 위한 것이 아닙니다.
if __name__ == '__main__':
    application.run()