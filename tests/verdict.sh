# Whether a test's output says it is red -- sourced by run.sh, which
# hands it to every worker, and read by source_suite_reads_red_test.py.
#
# said_red "<what the test printed>" returns 0 when it says red: a
# traceback, a line beginning with FAIL -- the closing "FAIL: ..." every
# test ends on, and the lines run.sh writes into a test's output itself
# -- or FAIL anywhere else, except on a check line whose verdict says ok.
#
# The exception is the whole point. Until 27.9.2026 FAIL anywhere in a
# line was red, so a check named after the word -- "run.sh reads a FAIL
# line as red" -- or an ok line quoting a red one in its numbers turned
# a green test red; five tests still spell it FA-IL in what they quote.
# A check line is "  %-58s %s %s": two spaces, the name padded to its
# width, the verdict, the numbers. The widths in use run from 52 to 64,
# so the verdict is the first "ok" or "FAIL" standing as a word from
# column 55 on; what stands before it is the name, what stands after it
# the numbers. A name longer than its width with "ok" or "FAIL" as a
# word past column 55 is misread -- the closing FAIL: line and the
# return code still say red, and those two are what a test answers by.
#
# One awk and not a grep per question: on the Windows builder every
# process is what a run pays for.
said_red() {
  printf '%s\n' "$1" | awk '
    /^Traceback/ || /^FAIL/ { red = 1; exit }
    !/FAIL/ { next }
    /^  / {
      tail = substr($0, 55)
      if (match(tail, / (ok|FAIL)( |$)/) \
          && substr(tail, RSTART + 1, 2) == "ok") next
    }
    { red = 1; exit }
    END { exit red ? 0 : 1 }'
}
