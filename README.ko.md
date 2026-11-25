# SOS My Feed

뉴스와 블로그의 RSS·Atom 피드를 구독하는 로컬 리더입니다.

## 시작하기

[GitHub 릴리스](https://github.com/gyedongjeon/sos-my-feed/releases)에서 운영체제에 맞는 설치 파일을 받으세요.

- **macOS (Apple Silicon)** — DMG를 열고 SOS My Feed를 응용 프로그램 폴더로 옮긴 뒤 실행하세요.
- **Windows (x64)** — Setup EXE로 설치한 뒤 시작 메뉴에서 SOS My Feed를 실행하세요. 기본 브라우저에서 리더가 열립니다. 사용을 마치면 콘솔 창을 닫아 서버를 종료하세요.

두 설치 파일에는 Python과 빌드된 화면이 포함되어 있습니다.

릴리스 ZIP을 받았다면 압축을 풀고 해당 폴더에서 Python 3.12로 `python3 backend/server.py`를 실행하세요. 화면 빌드 파일이 포함되어 있습니다.

소스에서 빌드하려면 Python 3.12와 Node.js 22.12 이상 및 npm을 준비하고 저장소 루트에서 실행하세요.

```sh
(cd frontend && npm ci && npm run build)
python3 backend/server.py
```

http://127.0.0.1:8000 에서 뉴스나 블로그의 피드 주소를 입력하고 **구독하기**를 누르세요. 전체 또는 출처별로 글을 보고 제목을 눌러 원문을 열 수 있습니다. **새로고침**을 누르면 최신 목록을 가져옵니다. 설정에서 구독 해제, 표시 언어, 테마를 변경할 수 있습니다. 구독 정보는 현재 브라우저에 저장됩니다.

개발 및 테스트 방법은 [영문 README](README.md)를 참고하세요.
