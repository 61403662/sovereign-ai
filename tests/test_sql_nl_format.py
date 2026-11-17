from sovereign_ai.bom.nl_format import SQL_NL_SYSTEM, maybe_naturalize_sql_answer


def test_nl_format_disabled_uses_template(monkeypatch, tmp_path):
    rag_dir = tmp_path / "config"
    rag_dir.mkdir()
    (rag_dir / "rag.yaml").write_text("sql_nl_format: false\nchunk_size: 1\n", encoding="utf-8")
    (rag_dir / "models.example.yaml").write_text(
        "ollama_base_url: http://127.0.0.1:11434\nchat_model: x\nembed_model: y\n",
        encoding="utf-8",
    )
    (tmp_path / "sovereign_ai").mkdir()
    # repo_root expects config/rag.yaml under tmp - pass root by patching load in call
    bom = {"answer": "TEMPLATE", "data": {"total": 26.7}}

    def fake_load_rag(root):
        return {"sql_nl_format": False}

    def fake_load_models(root):
        return {"ollama_base_url": "http://127.0.0.1:1", "chat_model": "c", "embed_model": "e"}

    monkeypatch.setattr("sovereign_ai.bom.nl_format.load_rag_config", fake_load_rag)
    monkeypatch.setattr("sovereign_ai.bom.nl_format.load_models_config", fake_load_models)
    assert maybe_naturalize_sql_answer("q", bom, root=tmp_path) == "TEMPLATE"


def test_sql_nl_system_mentions_json_rules():
    assert "JSON" in SQL_NL_SYSTEM
    assert "禁止" in SQL_NL_SYSTEM