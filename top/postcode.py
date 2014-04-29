__all__ = [
    "translate_postcode",
]
from top.utils.log import log


POSTCODE_MAP = {'NSW': {
                    'ranges': [
                        (1000, 1999),
                        (2000, 2599),
                        (2619, 2898),
                        (2921, 2999)],
                    'exceptions': [
                         2899]},
                'ACT': {
                    'ranges': [
                        (200, 299),
                        (2600, 2618),
                        (2900, 2920)],
                    'exceptions': []},
                'VIC': {
                    'ranges': [
                        (3000, 3999),
                        (8000, 8999)],
                    'exceptions': []},
                'QLD': {
                    'ranges': [
                        (4000, 4999),
                        (9000, 9999)],
                    'exceptions': []},
                'SA': {
                    'ranges': [
                        (5000, 5799),
                        (5800, 5999)],
                    'exceptions': []},
                'WA': {
                    'ranges': [
                        (6000, 6797),
                        (6800, 6999)],
                    'exceptions': []},
                'TAS': {
                    'ranges': [
                        (7000, 7999)],
                    'exceptions': []},
                'NT': {
                    'ranges': [
                        (800, 999)],
                    'exceptions': []}}


def translate_postcode(postcode):
    """Translate postcode information to state.

    **Args:**
        *postcode*: integer representing a postcode (for example, 3754)

    **Returns:**
        string representing the state of the translated postcode

    """
    log.debug('Translating raw postcode value: "%s" ...' % postcode)

    state = ''
    try:
        postcode = int(postcode)
    except ValueError, e:
        log.warn('Unable to translate postcode "%s"' % postcode)

    if isinstance(postcode, int):
        for postcode_state, postcode_ranges in POSTCODE_MAP.iteritems():
            for range in postcode_ranges.get('ranges'):
                if postcode >= range[0] and postcode <= range[1]:
                    state = postcode_state
                    break
            for exception in postcode_ranges.get('exceptions'):
                if postcode == exception:
                    state = postcode_state
                    break

            if state:
                break

        log.debug('Postcode/state - %d/"%s"' % (postcode, state))

    return state
