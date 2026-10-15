import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFilters } from '../../contexts/FilterContext';
import { Button, Icon } from '../../components/ui';
import { RxCross2, RxCheck} from "react-icons/rx";
import styles from './Filter.module.scss';
import utils from "../../scss/utils.module.scss";

const Filter = () => {
  const { setFilters, resetFilters, filters} = useFilters();
  const navigate = useNavigate();
  
  const [minCount, setMinCount] = useState<string>(filters.minCount?.toString() || '');
  const [maxCount, setMaxCount] = useState<string>(filters.maxCount?.toString() || '');
  const [minFloor, setMinFloor] = useState<string>(filters.minFloor?.toString() || '');
  const [maxFloor, setMaxFloor] = useState<string>(filters.maxFloor?.toString() || '');
  const [minPeople, setMinPeople] = useState<string>(filters.minPeople?.toString() || '');
  const [maxPeople, setMaxPeople] = useState<string>(filters.maxPeople?.toString() || '');
  const [minPeopleNow, setMinPeopleNow] = useState<string>(filters.minPeopleNow?.toString() || '');
  const [maxPeopleNow, setMaxPeopleNow] = useState<string>(filters.maxPeopleNow?.toString() || '');
  const [minSquare, setMinSquare] = useState<string>(filters.minSquare?.toString() || '');
  const [maxSquare, setMaxSquare] = useState<string>(filters.maxSquare?.toString() || '');
  const [city, setCity] = useState<string>(filters.city || '');

  const handleApplyFilters = () => {
    const newFilters = {
      minCount: minCount ? Number(minCount) : undefined,
      maxCount: maxCount ? Number(maxCount) : undefined,
      minFloor: minFloor ? Number(minFloor) : undefined,
      maxFloor: maxFloor ? Number(maxFloor) : undefined,
      minPeople: minPeople ? Number(minPeople) : undefined,
      maxPeople: maxPeople ? Number(maxPeople) : undefined,
      minPeopleNow: minPeopleNow ? Number(minPeopleNow) : undefined,
      maxPeopleNow: maxPeopleNow ? Number(maxPeopleNow) : undefined,
      minSquare: minSquare ? Number(minSquare) : undefined,
      maxSquare: maxSquare ? Number(maxSquare) : undefined,
      city: city || undefined,
    };
    
    setFilters(newFilters);
    navigate('/'); // Возвращаемся на страницу с квартирами
  };

  const handleReset = () => {
    setMinCount('');
    setMaxCount('');
    setMinFloor('');
    setMaxFloor('');
    setMinPeople('');
    setMaxPeople('');
    setMinPeopleNow('');
    setMaxPeopleNow('');
    setMinSquare('');
    setMaxSquare('');
    setCity('');
    resetFilters();
  };

  return (
    <div className={utils.container}>
    <div className={styles.filterPage}>    
      <div className={styles.filtersCard}>
        <label className={styles.filtersCard_label} >Количество комнат </label>
        <div className={styles.rangeInputs}>
          <input type="number" placeholder="От" value={minCount} onChange={(e) => setMinCount(e.target.value)}/>
          <span>—</span>
          <input type="number" placeholder="До" value={maxCount} onChange={(e) => setMaxCount(e.target.value)}/>
        </div>
      </div>

      <div className={styles.filtersCard}>
        <label className={styles.filtersCard_label} >Площадь (м²)</label>
        <div className={styles.rangeInputs}>
          <input type="number" placeholder="От" value={minSquare} onChange={(e) => setMinSquare(e.target.value)}/>
          <span>—</span>
          <input type="number" placeholder="До" value={maxSquare} onChange={(e) => setMaxSquare(e.target.value)}/>
        </div>
      </div>

      <div className={styles.filtersCard}>
        <label className={styles.filtersCard_label}>Город</label>
        <input type="text" placeholder="Например: Москва" className={styles.inputField} value={city} onChange={(e) => setCity(e.target.value)}/>
      </div>

      <div className={styles.filtersCard}>
        <label className={styles.filtersCard_label} >Этаж </label>
        <div className={styles.rangeInputs}>
          <input type="number" placeholder="От" value={minFloor} onChange={(e) => setMinFloor(e.target.value)}/>
          <span>—</span>
          <input type="number" placeholder="До" value={maxFloor} onChange={(e) => setMaxFloor(e.target.value)}/>
        </div>
      </div>

      <div className={styles.filtersCard}>
        <label className={styles.filtersCard_label} >Количество потенциальных соседей </label>
        <div className={styles.rangeInputs}>
          <input type="number" placeholder="От" value={minPeople} onChange={(e) => setMinPeople(e.target.value)}/>
          <span>—</span>
          <input type="number" placeholder="До" value={maxPeople} onChange={(e) => setMaxPeople(e.target.value)}/>
        </div>
      </div>

      <div className={styles.filtersCard}>
        <label className={styles.filtersCard_label} >Количество проживающих сейчас людей </label>
        <div className={styles.rangeInputs}>
          <input type="number" placeholder="От" value={minPeopleNow} onChange={(e) => setMinPeopleNow(e.target.value)}/>
          <span>—</span>
          <input type="number" placeholder="До" value={maxPeopleNow} onChange={(e) => setMaxPeopleNow(e.target.value)}/>
        </div>
      </div>

      <div className={styles.buttons}>
        <Button onClickAdditional={handleApplyFilters}> <Icon Icon = {RxCheck}/>Применить</Button>
        <Button onClickAdditional={handleReset}> <Icon Icon={RxCross2} /> Сбросить</Button>
      </div>
    </div>
    </div>
  );
};

export default Filter;