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
    await fetch("https://localhost:8080/"); // waits for 5
    console.log("test");
  }

  useEffect(() => {
    fetchRoute()
  }, [])

  return (
    <div>
      {/* { article?.Content }  */}
    </div>
  );
}