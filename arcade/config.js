// 오락실 설정. 피드백 저장 방식을 고른다.
//  - "local"   : 이 기기에만 저장 + '피드백 보내기' 누르면 요약 텍스트를 복사/공유 (계정 없이 바로 테스트 가능)
//  - "supabase": 모든 테스터의 피드백을 한 DB에 모음. arcade/feedback.sql 을 Supabase에 적용한 뒤 아래 두 값을 넣는다
// anon 키는 공개용 키라 웹페이지에 들어가도 되는 값이다(행 수준 보안으로 쓰기·읽기만 허용). service_role 키는 절대 넣지 않는다.
window.ARCADE_CONFIG = {
  feedback: "local",
  supabaseUrl: "",      // 예: https://xxxx.supabase.co
  supabaseAnonKey: "",  // 예: eyJhbGciOi...
  contact: "피드백 텍스트를 카톡으로 보내 주세요",
};
