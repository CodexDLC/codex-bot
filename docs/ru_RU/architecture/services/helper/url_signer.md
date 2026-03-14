# URL Signer — Безопасность Mini Apps

`URLSigner` — это специализированный инструмент для создания и проверки защищенных ссылок. Он незаменим при разработке Telegram Mini Apps (TWA), где необходимо гарантировать, что данные, переданные в приложение, не были подменены.

---

## 🛡 Зачем это нужно?

Когда бот открывает Mini App, он часто передает в URL параметры (например, `user_id`). Злоумышленник может попытаться изменить эти параметры в строке браузера.

`URLSigner` подписывает эти данные с помощью секретного ключа бота. Приложение на бэкенде может проверить эту подпись и убедиться, что ссылка была сформирована именно вашим ботом.

---

## ✍️ Использование в боте

Обычно `URLSigner` используется в оркестраторе для генерации кнопок типа `WebApp`:

```python
async def render_content(self, payload, director: Director):
    signer = director.container.url_signer
    app_url = signer.sign_params(
        base_url="https://game.codex.bot/start",
        params={"user_id": director.user_id}
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть игру", web_app=WebAppInfo(url=app_url))]
    ])

    return ViewResultDTO(text="Нажми кнопку, чтобы начать игру!", kb=kb)
```

---

## 🧭 Связанные разделы
- **[Helpers](./README.md)** — общая информация о вспомогательных инструментах.
- **[API: URL Signer](../../../../api/url_signer.md)** — техническое описание методов.
