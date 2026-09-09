# Apply a per-seat overlay onto a settings file.
#   jq -s -f overlay.jq <settings.json> <overlay.json>
#
# Everything merges recursively (so the overlay need only carry what differs),
# except autoMode.environment, which is spliced slot by slot: an overlay entry
# replaces the base entry sharing its "**Slot name**:" prefix, or is appended
# when the base has no such slot. That keeps the 21-slot array in one place —
# the overlay lists only the slots this seat answers differently.

.[0] as $base
| .[1] as $ov
| ($ov.autoMode.environment // []) as $slots
| ($base * ($ov | del(.autoMode.environment)))
| if $slots == [] then .
  else .autoMode.environment = reduce $slots[] as $e (
    $base.autoMode.environment // [];
    (($e | split(":")[0]) + ":") as $k
    | if any(.[]; startswith($k))
      then map(if startswith($k) then $e else . end)
      else . + [$e]
      end
  )
  end
