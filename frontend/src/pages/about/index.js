import { Title, Container, Main } from '../../components';
import styles from './styles.module.css';
import MetaTags from 'react-meta-tags';

const About = ({ updateOrders, orders }) => {
  return (
    <Main>
      <MetaTags>
        <title>О проекте</title>
        <meta name="description" content="Фудграм - О проекте" />
        <meta property="og:title" content="О проекте" />
      </MetaTags>

      <Container>
        <h1 className={styles.title}>Привет!</h1>
        <div className={styles.content}>
          <div>
            <h2 className={styles.subtitle}>Что это за сайт?</h2>
            <div className={styles.text}>
              <p className={styles.textItem}>
                Foodgram — веб-приложение для работы с рецептами. Я
                самостоятельно разработал ключевой функционал сервиса:
                регистрацию и авторизацию пользователей, создание и
                редактирование рецептов, загрузку изображений, подписки на
                авторов, добавление рецептов в избранное и корзину покупок.
              </p>
              <p className={styles.textItem}>
                Реализовал фильтрацию по тегам, короткие ссылки на рецепты,
                административную панель, импорт ингредиентов и формирование
                общего списка покупок на основе выбранных рецептов.
              </p>
            </div>
          </div>
          <aside>
            <h2 className={styles.additionalTitle}>Ссылки</h2>
            <div className={styles.text}>
              <p className={styles.textItem}>
                Код проекта находится тут -{' '}
                <a
                  href="https://github.com/srgtspkz/foodgram"
                  target="_blank"
                  className={styles.textLink}
                >
                  GitHub
                </a>
              </p>
              <p className={styles.textItem}>
                Автор проекта:{' '}
                <a
                  href="https://github.com/srgtspkz"
                  target="_blank"
                  className={styles.textLink}
                >
                  Сергей Цепилов
                </a>
              </p>
            </div>
          </aside>
        </div>
      </Container>
    </Main>
  );
};

export default About;
