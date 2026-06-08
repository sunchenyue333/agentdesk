import unittest

from app.agents.answer_generation import generate_grounded_answer
from app.services.chunking import split_markdown_text


class RagAnswerGenerationTests(unittest.TestCase):
    def test_markdown_chunking_keeps_heading_path(self):
        text = """# 登录与密码问题处理 SOP

## 用户忘记密码

用户忘记密码时，请引导用户点击 Forgot password。
用户需要输入注册邮箱。

## 退款

退款请求应按退款 SOP 处理。
"""

        chunks = split_markdown_text(text)

        self.assertGreaterEqual(len(chunks), 2)
        self.assertEqual(chunks[0].heading_path, ["登录与密码问题处理 SOP", "用户忘记密码"])
        self.assertIn("Forgot password", chunks[0].content)
        self.assertEqual(chunks[1].heading_path, ["登录与密码问题处理 SOP", "退款"])

    def test_password_reset_answer_excludes_unrelated_topics(self):
        chunks = [
            {
                "chunk_id": "chunk-password",
                "document_id": "doc-1",
                "document_title": "登录与密码问题处理 SOP",
                "heading": "登录与密码问题处理 SOP > 用户忘记密码",
                "heading_path": ["登录与密码问题处理 SOP", "用户忘记密码"],
                "content": (
                    "用户忘记密码时，请引导用户在登录页点击 Forgot password。"
                    "用户需要输入注册邮箱并提交重置请求。"
                    "系统会发送邮件链接，用户通过邮件链接重置密码。"
                    "重置链接有效期 30 分钟。"
                    "如果用户 10 分钟后仍未收到邮件，请创建 medium priority 工单。"
                ),
                "score": 0.95,
            },
            {
                "chunk_id": "chunk-noise",
                "document_id": "doc-1",
                "document_title": "混合示例集合",
                "heading": "混合示例集合",
                "heading_path": ["混合示例集合"],
                "content": "退款、数据删除、Starter Plan、重复扣款、系统加载慢、urgent priority。",
                "score": 0.80,
            },
        ]

        result = generate_grounded_answer("用户忘记密码应该怎么办？", chunks, openai_api_key=None)
        answer = result["answer"]

        self.assertEqual(result["answer_mode"], "mock")
        self.assertIn("点击 Forgot password", answer)
        self.assertIn("输入注册邮箱", answer)
        self.assertIn("通过邮件链接重置密码", answer)
        self.assertIn("30 分钟", answer)
        self.assertIn("10 分钟后仍未收到邮件", answer)
        self.assertIn("medium priority 工单", answer)
        self.assertNotIn("退款", answer)
        self.assertNotIn("数据删除", answer)
        self.assertNotIn("Starter Plan", answer)
        self.assertNotIn("重复扣款", answer)
        self.assertNotIn("系统加载慢", answer)
        self.assertNotIn("urgent priority", answer)


if __name__ == "__main__":
    unittest.main()
