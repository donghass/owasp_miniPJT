# OWASP Top 10 시나리오 매핑

목적: 실제 공격 코드 없이, 평가 가능한 A01~A10 점검 시나리오를 제공한다.

## 1. 서비스 내 위치

- 관리자 페이지 메뉴: `OWASP 시나리오`
- 경로:
  - 목록: `/security/scenarios`
  - 상세: `/security/scenarios/{scenario_id}`

## 2. 매핑표

| 코드 | 항목 | 본 서비스 점검 관점 | 증적 |
|---|---|---|---|
| A01 | Broken Access Control | 관리자/일반 사용자 경계, 타인 리소스 차단 | `/admin`, `/complaints/{id}` 접근 제어 로그 |
| A02 | Cryptographic Failures | 시크릿 관리, 해시 저장, 민감정보 노출 | 설정/로그 점검 결과 |
| A03 | Injection | 검색/입력 파라미터 처리 안정성 | ORM 사용 및 입력 검증 코드 |
| A04 | Insecure Design | 상태 전이/업무 규칙 누락 여부 | 민원 처리 플로우 점검 |
| A05 | Security Misconfiguration | 기본계정/디버그/오류노출 설정 | 환경 설정 점검 체크리스트 |
| A06 | Vulnerable Components | 의존성 버전 및 취약점 점검 절차 | requirements 및 점검 보고 |
| A07 | Auth Failures | 비밀번호/세션/로그인 정책 | 인증 테스트 결과 |
| A08 | Integrity Failures | 코드/설정/배포 무결성 관리 | 변경 이력/검증 절차 |
| A09 | Logging & Monitoring | 감사 로그와 모니터링 체계 | `/admin` 감사 로그 테이블 |
| A10 | SSRF | URL 요청 기능 추가 시 제약 정책 | 허용목록/내부망 차단 정책 |

## 3. 평가 운영 방법

1. 관리자 계정으로 `/security/scenarios` 접속
2. A01~A10 상세 페이지의 체크포인트 수행
3. 증적(화면 캡처, 로그, 테스트 결과)을 수집
4. 개선 전/후 비교 내용을 보고서에 반영

## 4. 안전 원칙

- 실서비스/공개망에서 공격 행위 재현 금지
- 실제 악용 가능한 취약 코드 삽입 금지
- 로컬 또는 폐쇄망 실습 환경에서만 검증 수행
