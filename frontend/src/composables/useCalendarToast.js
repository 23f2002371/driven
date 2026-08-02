import { ref } from 'vue';

const show = ref(false);
const message = ref('');

export function useCalendarToast() {
  const showCalendarToast = () => {
    message.value = 'Calendar invite will be available once backend integration is complete.';
    show.value = true;
    setTimeout(() => { show.value = false; }, 3000);
  };

  return { show, message, showCalendarToast };
}
