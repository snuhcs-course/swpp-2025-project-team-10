"""
Bootstrap the local catalog with popular Korean titles via Kakao Books API.
"""

from __future__ import annotations

from books.services.book_import_service import BookImportService
from books.services.kakao_book_pipeline import (
    ExternalBookAPIError,
    KakaoBookPipeline,
)
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()

DEFAULT_KEYWORDS = [
    # ===== 1. Modern & Contemporary Korean Fiction =====
    "소년이 온다",
    "채식주의자",
    "흰",
    "작별하지 않는다",
    "쇼코의 미소",
    "밝은 밤",
    "당신의 자리, 하나뿐",
    "산 자들",
    "서른, 잔치는 끝났다",
    "연애의 기억",
    "프롤로그",
    "피프티 피플",
    "내게 무해한 사람",
    "너무 한낮의 연애",
    "그 여름",
    "밤은 이야기하기 좋다",
    "이마를 비추는 별빛",
    "불안한 사람들",
    "달의 뒤편",
    "우리가 빛의 속도로 갈 수 없다면",
    "지구 끝의 온실",
    "방금 떠나온 세계",
    "한 사람을 위한 마음",
    "빛의 제국",
    "바깥은 여름",
    "나의 왼손은 왕, 오른손은 왕의 필경사",
    "알로하, 나의 엄마들",
    "일의 기쁨과 슬픔",
    "당신의 부탁",
    "독고솜에게 반하면",
    "살아야겠다",
    "미스 손탁",
    "벌거숭이들",
    "안녕 주정뱅이",
    "친밀한 이방인",
    "7년의 밤",
    "28",
    "종의 기원",
    "아가미",
    "여름, 어디선가 시체가",
    "오직 두 사람",
    "달의 아이",
    "모래알만 한 진실이라도",
    "이토록 평범한 미래",
    "우리가 함께 장마를 볼 수도 있겠어요",
    "서른의 반격",
    "불타는 여름",
    "그해, 여름 손님",
    "나를 보내지 마",
    "보통의 존재",
    "사월의 미, 칠월의 솔",
    "노말 시티",
    "선량한 차별주의자",
    "달콤한 나의 도시",
    "파리의 아파트",
    "영원히 서쪽",
    "단 하나의 문장",
    "비가 오면 열리는 상점",
    "딸에 대하여",
    "단명소녀 투쟁기",
    "불편한 편의점",
    "불편한 편의점 2",
    "달러구트 꿈 백화점",
    "달러구트 꿈 백화점 2",
    "달러구트 꿈 백화점 3",
    "사하맨션",
    "소설가의 일",
    "소년을 위로해줘",
    "문근영의 고백",
    "바깥은 여름",
    "하얼빈",
    "아몬드",
    "천 개의 파랑",
    "82년생 김지영",
    "파친코",
    "해리 포터",
    "기억의 밤",
    "죽고 싶지만 떡볶이는 먹고 싶어",
    "당신이 옳다",
    "프리즘",
    "돌이킬 수 없는 약속",
    "리틀 포레스트",
    "미드나잇 라이브러리",
    # ===== 2. Essays & Philosophy =====
    "여행의 이유",
    "죽은 자의 집 청소",
    "아침에는 죽음을 생각하는 것이 좋다",
    "무례한 사람에게 웃으며 대처하는 법",
    "살고 싶다는 농담",
    "지적 대화를 위한 넓고 얕은 지식",
    "세상에서 가장 짧은 철학 수업",
    "나는 나로 살기로 했다",
    "어른의 문답법",
    "시선으로부터",
    "사피엔스",
    "호모 데우스",
    "이기적 유전자",
    "코스모스",
    "생각의 지도",
    "언어의 온도",
    "감정 수업",
    "그림의 힘",
    "미움받을 용기",
    "자존감 수업",
    "죽음이란 무엇인가",
    "철학은 어떻게 삶의 무기가 되는가",
    "말 그릇",
    "보통의 언어들",
    "모든 것은 다 지나간다",
    "죽음의 수용소에서",
    "아주 작은 습관의 힘",
    "타인의 해석",
    "행복의 기원",
    "완벽하지 않은 것들에 대한 사랑",
    "공간이 만든 공간",
    "생각의 탄생",
    "철학의 위로",
    "불안",
    "나를 돌보는 시간",
    "명상록",
    "논어",
    "군주론",
    "수레바퀴 아래서",
    "이방인",
    "페스트",
    "인간 실격",
    "태백산맥",
    "토지",
    "난중일기",
    # ===== 3. Science Fiction / Fantasy =====
    "보건교사 안은영",
    "구미호 식당",
    "인더스트리",
    "클라우드 아틀라스",
    "설국열차",
    "드래곤라자",
    "퇴마록",
    "반지의 제왕",
    "나니아 연대기",
    "스노우 크래시",
    "어둠의 속도",
    "1984",
    "멋진 신세계",
    "나미야 잡화점의 기적",
    "파운데이션",
    "은하수를 여행하는 히치하이커",
    "레디 플레이어 원",
    "듄",
    "콘택트",
    "프랑켄슈타인",
    "닥터 모로의 섬",
    "시간을 달리는 소녀",
    "모든 것이 F로 통한다",
    "라플라스의 마녀",
    "용의자 X의 헌신",
    "백야행",
    "유성의 인연",
    "미 비포 유",
    "월드워Z",
    "방과 후",
    "해리 포터와 불사조 기사단",
    "해리 포터와 죽음의 성물",
    "오베라는 남자",
    "반지의 제왕: 왕의 귀환",
    "은하철도 999",
    "공각기동대",
    "사이버리아",
    "블레이드 러너",
    "어둠의 왼손",
    "꿈꾸는 기술",
    "스페이스 오디세이",
    "인터스텔라 소설판",
    "삼체",
    "암흑의 숲",
    "사신의 왕",
    "별의 계승자",
    "태양의 묘지",
    "행성 X",
    "시간의 주름",
    # ===== 4. Translated Classics =====
    "노르웨이의 숲",
    "1Q84",
    "색채가 없는 다자키 쓰쿠루",
    "해변의 카프카",
    "그리스인 조르바",
    "연금술사",
    "데미안",
    "싯다르타",
    "전쟁과 평화",
    "안나 카레니나",
    "죄와 벌",
    "카라마조프가의 형제들",
    "노인과 바다",
    "무기여 잘 있거라",
    "누구를 위하여 종은 울리나",
    "위대한 개츠비",
    "변신",
    "성",
    "심판",
    "동물농장",
    "시간 여행자의 아내",
    "오만과 편견",
    "제인 에어",
    "폭풍의 언덕",
    "작은 아씨들",
    "셜록 홈즈",
    "드라큘라",
    "지킬 박사와 하이드 씨",
    "도리언 그레이의 초상",
    "데카메론",
    "신곡",
    "오디세이",
    "일리아스",
    "플라톤의 향연",
    "국가",
    "윤리학",
    "니체의 말",
    "차라투스트라는 이렇게 말했다",
    "선악의 저편",
    "도덕의 계보",
    "정신분석 입문",
    "꿈의 해석",
    "사랑의 기술",
    "순수이성비판",
    "실천이성비판",
    "판단력비판",
    "존재와 시간",
    "역사란 무엇인가",
    "리바이어던",
    "사회계약론",
    "법의 정신",
    "정의의 원칙",
    # ===== 5. Korean Classics (고전문학 / 시 / 역사) =====
    "홍길동전",
    "춘향전",
    "심청전",
    "흥부전",
    "토끼전",
    "별주부전",
    "장화홍련전",
    "운영전",
    "구운몽",
    "사씨남정기",
    "허생전",
    "양반전",
    "호질",
    "임진록",
    "서유기 한국어판",
    "삼국유사",
    "삼국사기",
    "열하일기",
    "연암집",
    "동의보감",
    "조선왕조실록",
    "훈민정음 해례본",
    "난중일기",
    "격몽요결",
    "성학집요",
    "목민심서",
    "경세유표",
    "열녀전",
    "규중칠우쟁론기",
    "규원가",
    "가시리",
    "청산별곡",
    "정과정",
    "황진이 시조집",
    "이황 시문집",
    "이이 시문집",
    "박지원 산문선",
    "정약용 시문선",
    "김시습 금오신화",
    "연려실기술",
    "계녀서",
    "고려가요집",
    "동국신속삼강행실도",
    "송강가사집",
    "관동별곡",
    "사미인곡",
    "속미인곡",
    "춘추좌씨전",
    "논어집주",
    "퇴계집",
    "율곡집",
    "소학",
    "중용",
    "대학",
    "명심보감",
    "열국지 한국어판",
    "삼국지연의 한국어판",
    "수호지 한국어판",
    "서유기 한국어판",
    "동의보감",
    "난중일기 완역",
    "징비록",
    "연려실기술",
    "조선왕조실록 세종실록",
    "훈민정음 해례본 주석본",
    "삼강행실도",
    "오륜행실도",
    "효행록",
    "열녀전",
    "경국대전",
    "국조오례의",
    "대동여지도",
    "조선왕조실록 태조실록",
    "조선왕조실록 정조실록",
    "조선왕조실록 숙종실록",
    "조선왕조실록 광해군일기",
    "조선왕조실록 영조실록",
    "정조어제어필",
    "연암집 완역본",
    "택리지",
    "성호사설",
    "담헌서",
    "청학집",
    "고려사",
    "고려사절요",
    "동문선",
    "문집백선",
    "시경",
    "서경",
    "역경",
    "춘추",
    "예기",
    "중용",
    "대학",
    "주자어류",
    "고금소총",
    "통감강목",
    "삼국사기 완역본",
    "삼국유사 완역본",
    "용비어천가",
    "월인천강지곡",
    "훈민정음 언해본",
    "계몽전",
    "박인로 시선",
    "박목월 시집",
    "윤동주 시집",
    "서정주 시집",
    "김소월 시집",
    "정지용 시집",
    "한용운 시집",
    "김영랑 시집",
    "백석 시집",
    "신경림 시집",
    "황동규 시집",
    "기형도 시집",
    "이육사 시집",
    "윤동주 자화상",
    "서시",
    "별 헤는 밤",
    "진달래꽃",
    "님의 침묵",
    "초혼",
    "꽃",
    "광야",
    "눈 오는 지도",
    "청노루",
    "사슴",
    "국화 옆에서",
    "산문집 청록파",
    "사평역에서",
    "사랑하였으므로 행복하였네라",
    "참회록",
    "풀",
    "진달래꽃 시선집",
    "별 헤는 밤 시선집",
    "서시 윤동주",
    "님의 침묵 한용운",
    "국화 옆에서 김소월",
]


class Command(BaseCommand):
    help = (
        "Call the Kakao Books API with a curated list of popular Korean titles "
        "and seed the local database with the results."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "keywords",
            nargs="*",
            help=(
                "Optional override list of keywords/ISBNs. "
                "If omitted, a curated Korean list is used."
            ),
        )
        parser.add_argument(
            "--owner-id",
            type=int,
            help="ID of the user that will own the imported book copies.",
        )
        parser.add_argument(
            "--owner-email",
            help="Email of the user that will own the imported book copies.",
        )
        parser.add_argument(
            "--size",
            type=int,
            default=KakaoBookPipeline.DEFAULT_SIZE,
            help=(
                "Number of results to request from Kakao for each query "
                f"(default: {KakaoBookPipeline.DEFAULT_SIZE})."
            ),
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing metadata for matching publications.",
        )
        parser.add_argument(
            "--skip-copies",
            action="store_true",
            help="Only create/update BookPublication records (no BookCopy ownership).",
        )

    def handle(self, *args, **options):
        keywords = [kw.strip() for kw in options["keywords"] if kw.strip()]
        queries: list[str] = keywords or DEFAULT_KEYWORDS
        skip_copies: bool = options["skip_copies"]
        owner = None
        if not skip_copies:
            owner = self._resolve_owner(
                owner_id=options.get("owner_id"),
                owner_email=options.get("owner_email"),
            )
        size = options["size"]
        overwrite = options["overwrite"]

        if size <= 0:
            raise CommandError("The --size option must be a positive integer.")

        try:
            service = BookImportService(create_copies=not skip_copies)
        except Exception as exc:  # pragma: no cover - defensive
            raise CommandError(str(exc)) from exc

        aggregated = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "failures": 0,
        }

        for query in queries:
            try:
                summary = service.import_from_query(
                    query,
                    owner=owner,
                    size=size,
                    overwrite=overwrite,
                )
            except ExternalBookAPIError as exc:
                raise CommandError(f"Kakao API request failed: {exc}") from exc

            aggregated["processed"] += summary.processed
            aggregated["created"] += summary.created
            aggregated["updated"] += summary.updated
            aggregated["skipped"] += summary.skipped
            aggregated["failures"] += summary.failures

            self.stdout.write(
                self.style.SUCCESS(
                    f"[{query}] Processed {summary.processed}, "
                    f"created {summary.created}, "
                    f"updated {summary.updated}, "
                    f"skipped {summary.skipped}, "
                    f"failures {summary.failures}."
                )
            )

        totals_message = (
            "Total: processed {processed}, created {created}, "
            "updated {updated}, skipped {skipped}, failures {failures}."
        ).format(**aggregated)

        if aggregated["failures"]:
            self.stdout.write(self.style.WARNING(totals_message))
        else:
            self.stdout.write(self.style.SUCCESS(totals_message))

    def _resolve_owner(
        self,
        *,
        owner_id: int | None,
        owner_email: str | None,
    ) -> User:
        if owner_id is None and owner_email is None:
            raise CommandError(
                "Provide --owner-id or --owner-email to assign book ownership."
            )

        try:
            if owner_id is not None:
                return User.objects.get(id=owner_id)
            return User.objects.get(email=owner_email)
        except User.DoesNotExist as exc:
            raise CommandError(
                "Could not find the specified owner user."
            ) from exc
