export interface User {
  id: string;
  avatar?: string | undefined;
  name: string;
  surname: string;
  patronymic?: string;
  age: number;
  gender: string;
  badHabits: string;
  pet: string;
  hasRoommate: string;
}

export interface UserFormData {
  avatar?: string; 
  name: string;
  surname: string;
  patronymic?: string;
  age: number;
  gender: string;
  badHabits: string; 
  pet:string; 
  hasRoommate: string;
}
