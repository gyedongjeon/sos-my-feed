// Every text of the pages, in Korean. The keys are those of `en.ts`.
import type { MessageKey } from './index'

const ko: Record<MessageKey, string> = {
  'nav.feed': '내 피드',
  'nav.settings': '설정',
  'app.saveError': '브라우저에 저장할 수 없습니다.',

  'feed.titleFirst': '구독한 글을',
  'feed.titleSecond': '한곳에서.',
  'feed.intro': '뉴스와 블로그의 RSS · Atom 피드를 모아 읽으세요.',
  'feed.address': '피드 주소',
  'feed.subscribe': '구독하기',
  'feed.refresh': '새로고침',
  'feed.all': '전체',
  'feed.empty': '첫 피드를 구독해 보세요.',
  'feed.hint': '즐겨 읽는 사이트에서 RSS 주소를 복사해 위에 붙여 넣으세요.',
  'feed.noPosts': '아직 글이 없습니다.',
  'feed.failed': '피드를 불러오지 못했습니다. 주소와 연결을 확인하세요.',
  'feed.duplicate': '이미 구독한 피드입니다.',
  'feed.busy': '불러오는 중…',
  'feed.updated': '피드를 업데이트했습니다.',

  'reader.back': '피드로 돌아가기',
  'reader.previous': '이전',
  'reader.next': '다음',
  'reader.smaller': '글자 작게',
  'reader.larger': '글자 크게',
  'reader.summaryOnly': '본문을 불러올 수 없어 피드 요약을 표시합니다.',
  'reader.noBody': '읽을 수 있는 본문이나 피드 요약이 없습니다.',

  'settings.title': '설정',
  'settings.language': '표시 언어',
  'settings.theme': '화면 테마',
  'settings.auto': '시스템 설정',
  'settings.light': '라이트',
  'settings.dark': '다크',
  'settings.subscriptions': '구독 목록',
  'settings.remove': '구독 해제',
  'settings.cancel': '취소',
  'settings.confirm': '해제 확인',
}

export default ko
