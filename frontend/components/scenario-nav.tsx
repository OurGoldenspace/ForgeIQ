import Link from "next/link"

import { SCENARIOS } from "@/lib/api"

interface ScenarioNavProps {
  selected: string
}

export function ScenarioNav({ selected }: ScenarioNavProps) {
  return (
    <nav className="flex flex-wrap gap-2" aria-label="Scenarios">
      {SCENARIOS.map((scenario) => {
        const isActive = scenario.id === selected
        return (
          <Link
            key={scenario.id}
            href={`/?scenario=${scenario.id}`}
            className={
              isActive
                ? "rounded-md bg-zinc-900 px-3 py-1.5 text-sm text-white"
                : "rounded-md border border-zinc-200 bg-white px-3 py-1.5 text-sm text-zinc-700 hover:bg-zinc-100"
            }
          >
            {scenario.label}
          </Link>
        )
      })}
    </nav>
  )
}
