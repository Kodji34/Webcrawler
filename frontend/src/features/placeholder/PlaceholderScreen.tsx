import PendingActionsOutlinedIcon from '@mui/icons-material/PendingActionsOutlined'
import {
  Box,
  Chip,
  Grid,
  List,
  ListItem,
  Paper,
  Stack,
  Typography,
} from '@mui/material'
import { useTranslation } from 'react-i18next'

type PlaceholderScreenProps = {
  pageKey: 'researchQueue' | 'collections' | 'schedules' | 'settings'
}

export function PlaceholderScreen({ pageKey }: PlaceholderScreenProps) {
  const { t } = useTranslation()
  const checklist = t(`pages.${pageKey}.checklist`, {
    returnObjects: true,
  }) as string[]

  return (
    <Grid container spacing={2.5}>
      <Grid size={{ xs: 12, lg: 7 }}>
        <Paper className="rise-in" sx={{ p: 2.75 }}>
          <Stack spacing={2.5}>
            <Box>
              <Chip label={t('pages.phaseChip')} color="primary" size="small" />
              <Typography variant="h4" sx={{ mt: 1.25, mb: 0.75 }}>
                {t(`pages.${pageKey}.title`)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t(`pages.${pageKey}.description`)}
              </Typography>
            </Box>
            <List sx={{ p: 0 }}>
              {checklist.map((item) => (
                <ListItem key={item} sx={{ px: 0, py: 0.5 }}>
                  <PendingActionsOutlinedIcon
                    fontSize="small"
                    sx={{ color: 'primary.main', mr: 1.5 }}
                  />
                  <Typography variant="body2">{item}</Typography>
                </ListItem>
              ))}
            </List>
          </Stack>
        </Paper>
      </Grid>
      <Grid size={{ xs: 12, lg: 5 }}>
        <Paper className="rise-in" sx={{ p: 2.75, height: '100%' }}>
          <Stack spacing={2}>
            <Typography variant="h6">{t(`pages.${pageKey}.handoffTitle`)}</Typography>
            <Typography variant="body2" color="text.secondary">
              {t(`pages.${pageKey}.handoffBody`)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('pages.phaseBoundary')}
            </Typography>
          </Stack>
        </Paper>
      </Grid>
    </Grid>
  )
}
