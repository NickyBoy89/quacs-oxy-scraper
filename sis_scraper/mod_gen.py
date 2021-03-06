import json, math

from datetime import date
from itertools import combinations

def genmod(data, term):
    # Generate binary conflict output
    # day * 24 hours/day * 60minutes/hour = total buckets
    offset = lambda x: x * 24 * 60

    day_offsets = {
        "M": offset(0),
        "T": offset(1),
        "W": offset(2),
        "R": offset(3),
        "F": offset(4),
        "S": offset(5),
        "U": offset(6),
    }

    unique_ranges = set()
    get_date = lambda x: date(1, int(x[0]), int(x[1]))

    for dept in data:
        for course in dept["courses"]:
            for section in course["sections"]:
                for time in section["timeslots"]:
                    start = time["dateStart"].split("/")

                    if len(start) < 2:
                        continue
                    start_date = get_date(start)
                    unique_ranges.add(start_date)
    unique_ranges = list(unique_ranges)
    unique_ranges.sort(reverse=True)

    BITS_PER_SLICE = offset(len(day_offsets))
    BIT_VEC_SIZE = BITS_PER_SLICE * len(unique_ranges)

    conflicts = {}
    crn_to_courses = {}

    # A table consisting of lists of classes that conflict on the 'x'th bit
    sem_conflict_table = []

    for _ in range(BIT_VEC_SIZE):
        sem_conflict_table.append([])
    for dept in data:
        for course in dept["courses"]:
            for section in course["sections"]:
                conflict = [0] * BIT_VEC_SIZE
                for time in section["timeslots"]:
                    end = time["dateEnd"].split("/")
                    start = time["dateStart"].split("/")
                    if len(end) < 2 or len(start) < 2:
                        continue
                    my_end = get_date(end)
                    my_start = get_date(start)
                    for i, date_range in enumerate(unique_ranges):
                        # check to see if we are in this range
                        if my_end < date_range:
                            continue
                        if my_start > date_range:
                            continue

                        for day in time["days"]:
                            for hour in range(0, 2400, 100):
                                for minute in range(60):
                                    if (
                                        time["timeStart"] <= hour + minute
                                        and time["timeEnd"] > hour + minute
                                    ):
                                        minute_idx = minute
                                        hour_idx = hour // 100
                                        index = BITS_PER_SLICE * i + (
                                            day_offsets[day]
                                            + hour_idx * 60
                                            + minute_idx
                                        )
                                        conflict[index] = 1
                                        sem_conflict_table[index].append(
                                            section["crn"]
                                        )
                if sum(conflict) == 0:
                    continue

                crn_to_courses[section["crn"]] = course["id"]
                conflicts[section["crn"]] = conflict

    # Compute unnecessary conflict bits - where a bit is defined as unnecessary if its removal does not affect the result conflict checking
    # The following code computes a list of candidates that fit this criteria
    unnecessary_indices = set()

    for index1 in range(BIT_VEC_SIZE):
        for index2 in range(index1 + 1, BIT_VEC_SIZE):
            if (
                index2 not in unnecessary_indices
                and sem_conflict_table[index1] == sem_conflict_table[index2]
            ):
                unnecessary_indices.add(index2)

    # Reverse the list as to not break earlier offsets
    conflicts_to_prune = list(unnecessary_indices)
    conflicts_to_prune.sort(reverse=True)

    # Prune the bits in `conflicts_to_prune` from all the bitstrings
    for section_crn in conflicts:
        for bit in conflicts_to_prune:
            del conflicts[section_crn][bit]

    for x in conflicts_to_prune:
        del sem_conflict_table[x]

    BIT_VEC_SIZE -= len(unnecessary_indices)
    unnecessary_indices.clear()

    sem_conflict_dict = dict()

    for index1 in range(BIT_VEC_SIZE):
        for crn in sem_conflict_table[index1]:
            if crn not in sem_conflict_dict:
                sem_conflict_dict[crn] = set()

            sem_conflict_dict[crn].add(index1)

    # Optimization phase 2:
    # Now that we're on a (greatly) reduced working space, we can now prune using this
    # less efficient algorithm
    for index1 in range(BIT_VEC_SIZE):
        # We want all (unordered) pairs of conflicting courses on the bit `index1`
        pair_list = [pair for pair in combinations(sem_conflict_table[index1], 2)]

        # This part essentially tries to see if some other bit(s) other than the current one will create a conflict
        # for the conflicting classes in pair_list
        # If there is, we can safely discard this bit.
        pairs_to_delete = set()
        for pair in pair_list:
            table1 = sem_conflict_dict[pair[0]]
            table2 = sem_conflict_dict[pair[1]]
            for x in table1:
                if x != index1 and x in table2:
                    pairs_to_delete.add(pair)

        if len(pairs_to_delete) == len(pair_list):
            for pair in pair_list:
                table1 = sem_conflict_dict[pair[0]]
                table2 = sem_conflict_dict[pair[1]]

                table1.discard(index1)
                table2.discard(index1)

            unnecessary_indices.add(index1)

    # Reverse the list as to not break earlier offsets
    conflicts_to_prune = list(unnecessary_indices)
    conflicts_to_prune.sort(reverse=True)

    # Prune the bits in `conflicts_to_prune` from all the bitstrings
    for section_crn in conflicts:
        for bit in conflicts_to_prune:
            del conflicts[section_crn][bit]

        # Convert to a string for the quacs-rs rust codegen
        conflicts[section_crn] = "".join(str(x) for x in conflicts[section_crn])

    # Compute the proper bit vec length for quacs-rs
    BIT_VEC_SIZE = math.ceil((BIT_VEC_SIZE - len(unnecessary_indices)) / 64)
    with open(f"mod.rs", "w") as f:  # -{os.getenv("CURRENT_TERM")}
        f.write(
            """\
            //This file was automatically generated. Please do not modify it directly
            use ::phf::{{phf_map, Map}};

            pub const BIT_VEC_LEN: usize = """
                + str(BIT_VEC_SIZE)
                + """;

            pub static CRN_TIMES: Map<u32, [u64; BIT_VEC_LEN]> = phf_map! {
            """
        )

        for crn, conflict in conflicts.items():
            # print(f"{crn} {conflict}")
            rust_array = f"\t{crn}u32 => ["
            for i in range(0, BIT_VEC_SIZE * 64, 64):
                if i != 0:
                    rust_array += ", "
                rust_array += str(int(conflict[i : i + 64], 2))
            rust_array += "],\n"

            f.write(rust_array)

        f.write(
            """
            };

            pub static CRN_COURSES: Map<u32, &'static str> = phf_map! {
            """
        )

        for crn, course in crn_to_courses.items():
            f.write(f'\t{crn}u32 => "{course}",\n')

        f.write("};")

if __name__ == "__main__":
    term = "201601" # Spring (01) (the last 2 digits), of 2016 (first 4 digits)

    # Load in the courses
    with open("courses.json", "r") as courses_file:
        genmod(json.load(courses_file), term)
