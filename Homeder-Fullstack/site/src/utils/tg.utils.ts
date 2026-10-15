export const getTgId = (): string => {
  console.log('[getTgId] Начало получения tg_id');
  const urlParams = new URLSearchParams(window.location.search);
  const tgId = urlParams.get('tg_id');

  if (tgId) {
    console.log('[getTgId] tg_id из URL:', tgId);
    localStorage.setItem('tg_id', tgId); 
    return tgId;
  }
  
  const storedTgId = localStorage.getItem('tg_id');
  if (storedTgId) {
    console.log('[getTgId] tg_id из localStorage:', storedTgId);
    return storedTgId;
  }
  
  console.log('[getTgId] Используем test_user_123');
  return 'test_user_123';
};