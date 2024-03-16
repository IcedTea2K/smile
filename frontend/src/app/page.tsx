'use client'
import { use, useEffect, useState } from "react";

interface Article {
  Id	: string,
  Title: string,
  Desc: string,
  Content	: string,
}

export default function Home() {
  const [article, setArticle] = useState<Article>()

  const fetchRoute = async () => {
    const res = await fetch("http://localhost:8002/articles"); // waits for 5
    const yummy = await res.json()
    setArticle(yummy[1])
  }

  useEffect(() => {
    fetchRoute()
  }, [])

  return (
    <div>
      { article?.Content } 
    </div>
  );
}