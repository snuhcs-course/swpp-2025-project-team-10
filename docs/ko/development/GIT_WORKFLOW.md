# Git 워크플로우 가이드

이 문서는 SWPP AI Application 프로젝트의 Git 워크플로우, 브랜치 전략, 협업 방법을 설명합니다.

## 📋 목차

- [워크플로우 개요](#워크플로우-개요)
- [브랜치 전략](#브랜치-전략)
- [개발 프로세스](#개발-프로세스)
- [커밋 가이드라인](#커밋-가이드라인)
- [코드 리뷰](#코드-리뷰)
- [릴리스 프로세스](#릴리스-프로세스)
- [긴급 수정](#긴급-수정)
- [모범 사례](#모범-사례)

## 🔄 워크플로우 개요

우리는 **GitFlow 기반**의 워크플로우를 사용하여 안정적이고 체계적인 개발을 진행합니다.

```mermaid
gitGraph
    commit id: "Initial"
    branch dev
    checkout dev
    commit id: "Setup"
    
    branch feature/auth
    checkout feature/auth
    commit id: "Add login"
    commit id: "Add JWT"
    
    checkout dev
    merge feature/auth
    commit id: "Merge auth"
    
    checkout main
    merge dev
    commit id: "Release v1.0"
    tag: "v1.0.0"
```

### 핵심 원칙
1. **`main` 브랜치**: 항상 배포 가능한 상태 유지
2. **`dev` 브랜치**: 개발 통합 브랜치
3. **기능 브랜치**: 각 기능별로 독립적인 브랜치
4. **코드 리뷰**: 모든 변경사항은 리뷰를 거쳐 병합
5. **자동화**: CI/CD를 통한 자동 테스트 및 배포

## 🌳 브랜치 전략

### 메인 브랜치

#### `main` 브랜치
- **목적**: 프로덕션 배포용 안정 버전
- **보호**: 직접 푸시 금지, PR을 통해서만 병합
- **배포**: 자동으로 프로덕션 환경에 배포
- **태그**: 릴리스 시 버전 태그 생성

#### `dev` 브랜치
- **목적**: 개발 통합 및 테스트
- **병합**: 기능 브랜치들이 병합되는 곳
- **배포**: 자동으로 스테이징 환경에 배포
- **테스트**: 통합 테스트 실행

### 지원 브랜치

#### 기능 브랜치 (`feature/*`)
```bash
# 브랜치 생성
git checkout dev
git pull origin dev
git checkout -b feature/user-authentication

# 개발 완료 후
git push origin feature/user-authentication
# GitHub에서 dev로 PR 생성
```

#### 버그수정 브랜치 (`bugfix/*`)
```bash
# 버그수정 브랜치 생성
git checkout dev
git pull origin dev
git checkout -b bugfix/login-validation-error

# 수정 완료 후 PR 생성
```

#### 핫픽스 브랜치 (`hotfix/*`)
```bash
# 긴급 수정 브랜치 생성
git checkout main
git pull origin main
git checkout -b hotfix/security-vulnerability

# 수정 후 main과 dev 모두에 병합
```

## 🚀 개발 프로세스

### 1. 새로운 기능 개발

```bash
# 1. 최신 dev 브랜치로 업데이트
git checkout dev
git pull origin dev

# 2. 기능 브랜치 생성
git checkout -b feature/새로운기능

# 3. 개발 진행
# 코드 작성, 테스트 작성, 문서 업데이트

# 4. 정기적으로 dev와 동기화
git checkout dev
git pull origin dev
git checkout feature/새로운기능
git rebase dev

# 5. 커밋 및 푸시
git add .
git commit -m "feat(component): 새로운 기능 추가"
git push origin feature/새로운기능

# 6. Pull Request 생성
# GitHub에서 feature/새로운기능 → dev로 PR 생성
```

### 2. 코드 리뷰 및 병합

```bash
# 리뷰어가 승인한 후
# GitHub에서 "Squash and merge" 선택하여 병합

# 병합 후 로컬 정리
git checkout dev
git pull origin dev
git branch -d feature/새로운기능
git push origin --delete feature/새로운기능
```

### 3. 릴리스 준비

```bash
# 1. 릴리스 브랜치 생성
git checkout dev
git pull origin dev
git checkout -b release/v1.2.0

# 2. 버전 업데이트
# pyproject.toml, package.json 등에서 버전 수정
# CHANGELOG.md 업데이트

# 3. 릴리스 테스트
make test
make build

# 4. main으로 PR 생성 및 병합
# 5. 태그 생성
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

## 📝 커밋 가이드라인

### 커밋 메시지 형식
```
<타입>[선택적 스코프]: <설명>

[선택적 본문]

[선택적 푸터]
```

### 커밋 타입
- **feat**: 새로운 기능
- **fix**: 버그 수정
- **docs**: 문서 변경
- **style**: 코드 스타일 변경 (포맷팅 등)
- **refactor**: 코드 리팩토링
- **test**: 테스트 추가/수정
- **chore**: 빌드 프로세스나 도구 변경

### 좋은 커밋 메시지 예시
```bash
# 좋은 예
feat(auth): JWT 토큰 갱신 기능 추가
fix(ui): 모바일에서 버튼 정렬 오류 수정
docs(api): 사용자 인증 API 문서 업데이트
refactor(db): 사용자 쿼리 성능 최적화

# 나쁜 예
fix: 버그 수정
update: 코드 업데이트
feat: 새 기능
```

### 커밋 크기
- **작은 커밋**: 하나의 논리적 변경사항만 포함
- **원자적 커밋**: 각 커밋은 독립적으로 의미가 있어야 함
- **테스트 가능**: 각 커밋 후에도 코드가 작동해야 함

## 👥 코드 리뷰

### 리뷰 요청 전 체크리스트
- [ ] 코드가 컴파일되고 테스트가 통과함
- [ ] 코딩 표준을 준수함
- [ ] 적절한 테스트가 작성됨
- [ ] 문서가 업데이트됨
- [ ] 커밋 메시지가 규칙을 따름

### Pull Request 템플릿
```markdown
## 변경사항 설명
이 PR에서 수행한 작업에 대한 간단한 설명

## 변경 타입
- [ ] 새로운 기능
- [ ] 버그 수정
- [ ] 문서 업데이트
- [ ] 리팩토링
- [ ] 성능 개선

## 테스트
- [ ] 단위 테스트 추가/업데이트
- [ ] 통합 테스트 통과
- [ ] 수동 테스트 완료

## 체크리스트
- [ ] 코드 스타일 가이드 준수
- [ ] 자체 리뷰 완료
- [ ] 관련 문서 업데이트
- [ ] 테스트 커버리지 유지/개선

## 관련 이슈
Closes #123
```

### 리뷰 가이드라인

#### 리뷰어를 위한 가이드
1. **건설적인 피드백**: 문제점과 함께 해결 방안 제시
2. **명확한 의사소통**: 의견과 요구사항을 명확히 구분
3. **신속한 리뷰**: 24시간 내 첫 리뷰 완료
4. **전체적인 관점**: 코드 품질, 성능, 보안 고려

#### 작성자를 위한 가이드
1. **상세한 설명**: PR 설명에 충분한 컨텍스트 제공
2. **작은 PR**: 리뷰하기 쉬운 크기로 유지 (400줄 이하)
3. **신속한 대응**: 리뷰 피드백에 빠르게 응답
4. **학습 자세**: 피드백을 통해 개선점 학습

### 리뷰 승인 기준
- **기능성**: 요구사항을 올바르게 구현
- **코드 품질**: 가독성, 유지보수성, 성능
- **테스트**: 적절한 테스트 커버리지
- **보안**: 보안 취약점 없음
- **문서**: 필요한 문서 업데이트

## 🚀 릴리스 프로세스

### 릴리스 계획
1. **기능 완료**: dev 브랜치에서 모든 기능 개발 완료
2. **통합 테스트**: 전체 시스템 테스트 실행
3. **릴리스 브랜치**: release/vX.Y.Z 브랜치 생성
4. **버전 업데이트**: 버전 번호 및 변경로그 업데이트
5. **최종 테스트**: 릴리스 후보에 대한 최종 검증

### 릴리스 실행
```bash
# 1. 릴리스 브랜치에서 최종 준비
git checkout release/v1.2.0
git add .
git commit -m "chore(release): v1.2.0 릴리스 준비"

# 2. main으로 병합
# GitHub에서 release/v1.2.0 → main PR 생성 및 병합

# 3. 태그 생성 및 푸시
git checkout main
git pull origin main
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0

# 4. dev로 백포트
# GitHub에서 main → dev PR 생성 및 병합
```

### 릴리스 후 작업
1. **배포 모니터링**: 프로덕션 환경 상태 확인
2. **이슈 대응**: 릴리스 관련 이슈 신속 처리
3. **문서 업데이트**: 릴리스 노트 및 사용자 문서 업데이트
4. **회고**: 릴리스 프로세스 개선점 논의

## 🚨 긴급 수정 (Hotfix)

### 긴급 상황 대응
```bash
# 1. main에서 핫픽스 브랜치 생성
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# 2. 최소한의 수정 작업
# 문제가 되는 부분만 수정

# 3. 테스트 및 검증
make test
# 수동 테스트로 수정사항 확인

# 4. main으로 긴급 병합
# GitHub에서 hotfix → main 긴급 PR 생성
# 최소 1명의 시니어 개발자 승인 후 병합

# 5. 즉시 배포
# CI/CD 파이프라인을 통한 자동 배포

# 6. dev로 백포트
# main → dev PR 생성하여 변경사항 동기화
```

### 핫픽스 기준
- **심각도**: 프로덕션 서비스에 심각한 영향
- **긴급성**: 즉시 수정이 필요한 상황
- **범위**: 최소한의 변경으로 문제 해결

## 📋 모범 사례

### 브랜치 관리
1. **정기적 동기화**: 기능 브랜치를 dev와 자주 동기화
2. **브랜치 정리**: 병합된 브랜치는 즉시 삭제
3. **명명 규칙**: 일관된 브랜치 명명 규칙 준수
4. **수명 관리**: 장기간 유지되는 브랜치 최소화

### 커밋 관리
1. **논리적 단위**: 관련된 변경사항을 하나의 커밋으로
2. **의미있는 메시지**: 변경 이유와 내용을 명확히 기술
3. **작은 커밋**: 리뷰와 디버깅이 쉬운 크기 유지
4. **테스트 포함**: 각 커밋에 관련 테스트 포함

### 협업 방법
1. **소통**: 작업 시작 전 팀원들과 소통
2. **문서화**: 중요한 결정사항은 문서로 기록
3. **지식 공유**: 코드 리뷰를 통한 지식 공유
4. **지속적 개선**: 프로세스 개선점 지속적 논의

### 품질 관리
1. **자동화**: CI/CD를 통한 자동 품질 검사
2. **테스트**: 충분한 테스트 커버리지 유지
3. **코드 리뷰**: 모든 변경사항에 대한 리뷰
4. **모니터링**: 배포 후 시스템 상태 모니터링

## 🔧 도구 및 자동화

### Git Hooks
```bash
# Pre-commit hook 설정
pre-commit install

# 커밋 전 자동 실행:
# - 코드 포맷팅
# - 린팅 검사
# - 단위 테스트
```

### GitHub Actions
- **CI**: 모든 PR에 대한 자동 테스트
- **CD**: main 브랜치 병합 시 자동 배포
- **품질 검사**: 코드 커버리지, 보안 스캔
- **알림**: Slack 통합으로 팀 알림

### 유용한 Git 명령어
```bash
# 브랜치 상태 확인
git status
git branch -v

# 변경사항 확인
git diff
git log --oneline --graph

# 브랜치 정리
git branch --merged | grep -v main | xargs git branch -d
git remote prune origin

# 커밋 수정
git commit --amend
git rebase -i HEAD~3
```

---

**이 워크플로우를 따라 체계적이고 안전한 개발을 진행하세요! 궁금한 점이 있으면 팀에 문의하세요.** 🚀
